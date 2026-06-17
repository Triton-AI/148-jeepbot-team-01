#include <Arduino.h>
#include <Joystick.h>
#include <FUTABA_SBUS.h>
#include "utils/SBusTracker.h"
// #include <Streaming.h>


// Compile-time debug logging.
// To enable debug serial output, define the `DEBUG_LOG` macro in your build flags.
// For PlatformIO add this to your environment in `platformio.ini`:
//
// [env:your_env]
// build_flags = -DDEBUG_LOG
//
// Note: On some boards the Serial interface may conflict with USB HID functionality
// (e.g., when emulating a joystick). Only enable serial debug while testing.
#if defined(DEBUG_LOG)
#define DEBUG_BEGIN(baud) Serial.begin(baud)
#define DEBUG_PRINT(val) Serial.print(val)
#define DEBUG_PRINTLN(val) Serial.println(val)
#else
#define DEBUG_BEGIN(baud) do {} while (0)
#define DEBUG_PRINT(val) do {} while (0)
#define DEBUG_PRINTLN(val) do {} while (0)
#endif

#define MIN_SIGNAL 190
#define MAX_SIGNAL 1790

#define ACTIVE_SIGNAL 1792
#define RELEASED_SIGNAL 192
#define MAJORITY_THRESH ( (HISTORY_SIZE / 2 + 1) * ACTIVE_SIGNAL) / HISTORY_SIZE

#define EMA_ALPHA 0.12f // tuned: slightly more smoothing for stability
#define DEBOUNCE_COUNT 3 // tuned: require 3 consecutive confirmations to change mode

#define XAXIS_CHANNEL 3
#define YAXIS_CHANNEL 2
#define RX_CHANNEL 0
#define RY_CHANNEL 1
#define L_TRI_SWITCH_CHANNEL 5
#define R_TRI_SWITCH_CHANNEL 6
#define LBUTTON_CHANNEL 4
#define RBUTTON_CHANNEL 7
#define SE_BUTTON_CHANNEL 8

enum TriSwitchMode
{
    DOWN = 0,
    MID = 1,
    UP = 2,
};

enum ButtonMode
{
    OFF = 0,
    ON = 1,
};

struct Translation
{
    double normalize(int analogValue);
    TriSwitchMode getTriSwitchMode(int TriVal);
    ButtonMode get_button_state(int estimated);
};

// TRANSLATION
double Translation::normalize(int analogValue) 
{
    if (analogValue > 1800)
        analogValue = 1800;
    if (analogValue < 174)
        analogValue = 174;
    analogValue -= 992;
    return analogValue >= 0 ? (double(analogValue) / (1800 - 992))
                            : (double(analogValue) / (992 - 174));
}
TriSwitchMode Translation::getTriSwitchMode(int TriVal)
{
    double TriVal_norm = normalize(TriVal);
    if (TriVal_norm < -0.5)
        return DOWN;
    else if (TriVal_norm > 0.4)
        return UP;
    else
        return MID;
}
ButtonMode Translation::get_button_state(int estimated) {
    if (estimated > MAJORITY_THRESH) {
      return ON;
    } else {
      return OFF;
    }
}

// Hysteresis for tri-switch mode to prevent flapping near thresholds
static TriSwitchMode lastLMode = MID;
static TriSwitchMode lastRMode = MID;
// Debounce counters for confirming a new mode before committing
static int l_mode_counter = 0;
static int r_mode_counter = 0;

// Median-of-3 buffers for L and R raw samples
static long l_raw_buf[3] = {0};
static long r_raw_buf[3] = {0};
static int l_raw_idx = 0;
static int r_raw_idx = 0;

// Exit confirmation counters: require several consecutive exit samples to leave UP/DOWN
static int l_exit_counter = 0;
static int r_exit_counter = 0;

// Button hysteresis/debounce state (use normalized values like tri-switches)
static ButtonMode l_button_state = OFF;
static ButtonMode r_button_state = OFF;
static int l_button_mode_counter = 0;
static int r_button_mode_counter = 0;
static int l_button_exit_counter = 0;
static int r_button_exit_counter = 0;

// Button thresholds (normalized), same pattern as tri-switch
const static double button_enter = 0.20;
const static double button_exit = -0.20;

// Update a binary button using normalized input with enter/exit hysteresis and DEBOUNCE_COUNT
static ButtonMode update_button_hysteresis(Translation &translator, int estimated,
                                           ButtonMode &state, int &mode_counter, int &exit_counter,
                                           const char *name) {
  double n = translator.normalize(estimated);
  ButtonMode old = state;
  if (state == ON) {
    if (n < button_exit) {
      if (++exit_counter >= DEBOUNCE_COUNT) {
        state = OFF;
        exit_counter = 0;
      }
    } else {
      exit_counter = 0;
    }
  } else { // OFF
    if (n > button_enter) {
      if (++mode_counter >= DEBOUNCE_COUNT) {
        state = ON;
        mode_counter = 0;
      }
    } else {
      mode_counter = 0;
    }
  }
  if (state != old) {
#if defined(DEBUG_LOG)
    DEBUG_PRINT(name); DEBUG_PRINT(" button: "); DEBUG_PRINT(old == OFF ? "OFF" : "ON"); DEBUG_PRINT(" -> "); DEBUG_PRINTLN(state == OFF ? "OFF" : "ON");
#endif
  }
  return state;
}

TriSwitchMode getTriSwitchModeWithHysteresis(Translation &translator, long rawValue, TriSwitchMode &lastMode) {
  double n = translator.normalize(static_cast<int>(rawValue));
  // thresholds tuned relative to Translation::getTriSwitchMode thresholds
  const static double up_enter = 0.45;
  const static double up_exit = 0.15; // tuned: require a clearer drop to exit UP
  const static double down_enter = -0.55;
  const static double down_exit = -0.15;

  if (lastMode == UP) {
    // pick correct exit counter for this switch
    int *exit_counter = nullptr;
    if (&lastMode == &lastLMode) exit_counter = &l_exit_counter;
    else if (&lastMode == &lastRMode) exit_counter = &r_exit_counter;

    if (n < up_exit) {
      // require consecutive exit confirmations
      if (exit_counter) {
        if (++(*exit_counter) >= DEBOUNCE_COUNT) {
          lastMode = MID;
          *exit_counter = 0;
        }
      } else {
        // fallback: immediate
        lastMode = MID;
      }
    } else {
      if (exit_counter) *exit_counter = 0;
    }
    return lastMode;
  }
  if (lastMode == DOWN) {
    // pick correct exit counter for this switch
    int *exit_counter = nullptr;
    if (&lastMode == &lastLMode) exit_counter = &l_exit_counter;
    else if (&lastMode == &lastRMode) exit_counter = &r_exit_counter;

    if (n > down_exit) {
      if (exit_counter) {
        if (++(*exit_counter) >= DEBOUNCE_COUNT) {
          lastMode = MID;
          *exit_counter = 0;
        }
      } else {
        lastMode = MID;
      }
    } else {
      if (exit_counter) *exit_counter = 0;
    }
    return lastMode;
  }

  // lastMode == MID
  // Candidate mode based on thresholds
  TriSwitchMode candidate;
  if (n > up_enter) {
    candidate = UP;
  } else if (n < down_enter) {
    candidate = DOWN;
  } else {
    candidate = MID;
  }

  // Debounce: require DEBOUNCE_COUNT consecutive candidate readings before committing
  int *counter = nullptr;
  if (&lastMode == &lastLMode) counter = &l_mode_counter;
  else if (&lastMode == &lastRMode) counter = &r_mode_counter;

  if (counter) {
    if (candidate == lastMode) {
      *counter = 0; // already in this mode
    } else {
      (*counter)++;
      if (*counter >= DEBOUNCE_COUNT) {
        lastMode = candidate;
        *counter = 0;
      }
    }
  } else {
    // Fallback: commit immediately
    lastMode = candidate;
  }

  return lastMode;
}

// Helper to convert mode to human-readable string for debug logging
static const char* triModeToString(TriSwitchMode m) {
  switch (m) {
    case DOWN: return "DOWN";
    case MID: return "MID";
    case UP: return "UP";
    default: return "UNKNOWN";
  }
}

// Variant with debug logging (prints when the mode changes). Name is used to indicate L/R switch.
// Helper to compute normalized value for logging
static double normalize_for_log(Translation &translator, long rawValue) {
  return translator.normalize(static_cast<int>(rawValue));
}

TriSwitchMode getTriSwitchModeWithHysteresis(Translation &translator, long rawValue, TriSwitchMode &lastMode, const char* name) {
  TriSwitchMode oldMode = lastMode;
  TriSwitchMode newMode = getTriSwitchModeWithHysteresis(translator, rawValue, lastMode);
  if (newMode != oldMode) {
    double n = normalize_for_log(translator, rawValue);
    DEBUG_PRINT(name);
    DEBUG_PRINT(" change: ");
    DEBUG_PRINT(triModeToString(oldMode));
    DEBUG_PRINT(" -> ");
    DEBUG_PRINT(triModeToString(newMode));
    DEBUG_PRINT(" | raw=");
    DEBUG_PRINT(rawValue);
    DEBUG_PRINT(" norm=");
    DEBUG_PRINTLN(n);
  }
  return newMode;
}

// Exponential Moving Average (IIR) helper
// alpha: smoothing factor in (0,1). Smaller alpha = more smoothing.
static float l_est_ema = 0.0f;
static float r_est_ema = 0.0f;
static float se_est_ema = 0.0f;
static bool l_est_ema_init = false;
static bool r_est_ema_init = false;
static bool se_est_ema_init = false;

static long ema_update(float &state, bool &inited, const float alpha, long sample) {
  if (!inited) {
    state = (float)sample;
    inited = true;
  } else {
    state = alpha * (float)sample + (1.0f - alpha) * state;
  }
  return (long)(state + 0.5f);
}

Translation Map;

Joystick_ Joystick(JOYSTICK_DEFAULT_REPORT_ID,JOYSTICK_TYPE_MULTI_AXIS,
  11, 0,                  // Button Count, Hat Switch Count
  true, true, false,     // X and Y, but no Z Axis
  true, true, false,   // No Rx, Ry, or Rz
  true, true,          // No rudder or throttle
  false, false, false);  // No accelerator, brake, or steering

FUTABA_SBUS sBus;

SBusTracker xAxisTracker;
SBusTracker yAxisTracker;
SBusTracker rxTracker;
SBusTracker ryTracker;
SBusTracker lTriSwitchTracker;
SBusTracker rTriSwitchTracker;
SBusTracker lButTracker;
SBusTracker rButTracker;
SBusTracker SEButTracker;

void setup() {

  //Set pinout
  pinMode(8, OUTPUT);
  // Initialize Serial only when debug logging is enabled
  DEBUG_BEGIN(115200);
  // Configure JoyStick
  Joystick.setXAxisRange(MIN_SIGNAL, MAX_SIGNAL);
  Joystick.setYAxisRange(MIN_SIGNAL, MAX_SIGNAL);
  Joystick.setRxAxisRange(MIN_SIGNAL, MAX_SIGNAL);
  Joystick.setRyAxisRange(MIN_SIGNAL, MAX_SIGNAL);
  Joystick.setThrottleRange(MIN_SIGNAL, MAX_SIGNAL);
  Joystick.setRudderRange(MIN_SIGNAL, MAX_SIGNAL);
  
  // Begin!!!
  Joystick.begin();
  sBus.begin();
}

void update_trackers(FUTABA_SBUS & sBus) {
  xAxisTracker.add(sBus.channels[XAXIS_CHANNEL]);
  yAxisTracker.add(sBus.channels[YAXIS_CHANNEL]);
  rxTracker.add(sBus.channels[RX_CHANNEL]);
  ryTracker.add(sBus.channels[RY_CHANNEL]);
  lTriSwitchTracker.add(sBus.channels[L_TRI_SWITCH_CHANNEL]);
  rTriSwitchTracker.add(sBus.channels[R_TRI_SWITCH_CHANNEL]);
  lButTracker.add(sBus.channels[LBUTTON_CHANNEL]);
  rButTracker.add(sBus.channels[RBUTTON_CHANNEL]);
  SEButTracker.add(sBus.channels[SE_BUTTON_CHANNEL]);
}

static int modeIndex = -1;
static int lastModeIndex = -1;
void loop() {
  sBus.FeedLine();
  if (sBus.toChannels == 1){
    sBus.UpdateChannels();
    sBus.toChannels = 0; 

    update_trackers(sBus);

    Joystick.setXAxis(xAxisTracker.get_estimated());
    Joystick.setYAxis(yAxisTracker.get_estimated());
    Joystick.setRxAxis(rxTracker.get_estimated());
    Joystick.setRyAxis(ryTracker.get_estimated());
    Joystick.setThrottle(lTriSwitchTracker.get_estimated());
    Joystick.setRudder(rTriSwitchTracker.get_estimated());
    // Use normalized enter/exit hysteresis + debounce for buttons (same mech as tri-switch)
    update_button_hysteresis(Map, lButTracker.get_estimated(), l_button_state, l_button_mode_counter, l_button_exit_counter, "LBtn");
    update_button_hysteresis(Map, rButTracker.get_estimated(), r_button_state, r_button_mode_counter, r_button_exit_counter, "RBtn");
    Joystick.setButton(0, l_button_state);
    Joystick.setButton(1, r_button_state);

    // Apply the exponential moving average filter
    long l_est = ema_update(l_est_ema, l_est_ema_init, EMA_ALPHA, lTriSwitchTracker.get_estimated());
    long r_est = ema_update(r_est_ema, r_est_ema_init, EMA_ALPHA, rTriSwitchTracker.get_estimated());
    int se_est = static_cast<int>(ema_update(se_est_ema, se_est_ema_init, EMA_ALPHA, SEButTracker.get_estimated()));

    // Median-of-3 prefilter for L and R raw estimates
    l_raw_buf[l_raw_idx] = l_est;
    l_raw_idx = (l_raw_idx + 1) % 3;
    long l_med_vals[3] = { l_raw_buf[0], l_raw_buf[1], l_raw_buf[2] };
    // sort 3 values to get median
    for (int i = 0; i < 2; ++i) for (int j = i+1; j < 3; ++j) if (l_med_vals[i] > l_med_vals[j]) { long t = l_med_vals[i]; l_med_vals[i] = l_med_vals[j]; l_med_vals[j] = t; }
    long l_med = l_med_vals[1];

    r_raw_buf[r_raw_idx] = r_est;
    r_raw_idx = (r_raw_idx + 1) % 3;
    long r_med_vals[3] = { r_raw_buf[0], r_raw_buf[1], r_raw_buf[2] };
    for (int i = 0; i < 2; ++i) for (int j = i+1; j < 3; ++j) if (r_med_vals[i] > r_med_vals[j]) { long t = r_med_vals[i]; r_med_vals[i] = r_med_vals[j]; r_med_vals[j] = t; }
    long r_med = r_med_vals[1];

    // Combine the two switch modes (L_TRI_SWITCH and R_TRI_SWITCH) into a single index (0-8)
    TriSwitchMode lMode = getTriSwitchModeWithHysteresis(Map, l_med, lastLMode, "L");
    TriSwitchMode rMode = getTriSwitchModeWithHysteresis(Map, r_med, lastRMode, "R");

    modeIndex = (static_cast<int>(lMode) * 3) + static_cast<int>(rMode);

    // Use the modeIndex (0-8) to select the corresponding button state (2-10)
    // L: DOWN, MID, UP = 0, 1, 2
    // R: DOWN, MID, UP = 0, 1, 2
    // modeIndex = L * 3 + R
    if (modeIndex >= 0 && modeIndex <= 8) {
      Joystick.setButton(modeIndex + 2, Map.get_button_state(se_est));
    }

    // Only update if modeIndex has changed
    if (modeIndex != lastModeIndex) {
      if (lastModeIndex >= 0 && lastModeIndex <= 8) Joystick.setButton(lastModeIndex + 2, OFF);
      lastModeIndex = modeIndex;
#if defined(DEBUG_LOG)
      DEBUG_PRINT("Mode Index: "); DEBUG_PRINTLN(modeIndex);
      DEBUG_PRINT("SE Button State: "); DEBUG_PRINTLN(se_est);
#endif
    }
    
    if (lButTracker.get_estimated() > MAJORITY_THRESH || 
        rButTracker.get_estimated() > MAJORITY_THRESH)
    {
      digitalWrite(8, HIGH);
    }
    else{
      digitalWrite(8, LOW);
    }
  }
}