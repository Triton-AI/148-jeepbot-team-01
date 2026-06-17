from donkeycar.parts.controller import Joystick, JoystickController


class MyJoystick(Joystick):
    #An interface to a physical joystick available at /dev/input/js0
    def __init__(self, *args, **kwargs):
        super(MyJoystick, self).__init__(*args, **kwargs)


        self.button_names = {
            # 0x100 : 'SA',
            # 0x101 : 'SD',
            0x102 : 'SE_2',
            0x103 : 'SE_3',
            0x104 : 'SE_4',
            0x105 : 'SE_5',
            0x106 : 'SE_6',
            0x107 : 'SE_7',
            0x108 : 'SE_8',
            0x109 : 'SE_9',
            0x10a : 'SE_10',
        }


        self.axis_names = {
            0x0 : 'Rudder',
            0x1 : 'Throttle',
            0x3 : 'Aileron',
            0x4 : 'Elevator',
        }



class MyJoystickController(JoystickController):
    #A Controller object that maps inputs to actions
    def __init__(self, *args, **kwargs):
        super(MyJoystickController, self).__init__(*args, **kwargs)


    def init_js(self):
        #attempt to init joystick
        try:
            self.js = MyJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None


    def init_trigger_maps(self):
        #init set of mapping from buttons to function calls

        self.button_down_trigger_map = {
            # note that back is the position of pressing the part closer to the operator down
            # forward is clicked the far part down
            'SE_2' : self.toggle_mode,
            'SE_3' : self.erase_last_N_records,
            'SE_4' : self.toggle_manual_recording,
            # 'SE_5' : self.decrease_max_throttle,
            'SE_6' : self.toggle_constant_throttle,
            # 'SE_7' : self.increase_max_throttle,
            'SE_8' : self.emergency_stop,
        }


        self.axis_trigger_map = {
            'Rudder' : self.set_steering,
            'Elevator' : self.set_inverted_throttle,
        }

    def set_inverted_throttle(self, axis_val):
        self.set_throttle(-axis_val)
