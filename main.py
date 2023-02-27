import customtkinter as ctk
from tkinter import filedialog as fd
from tkinter import LEFT, END
from functools import partial
from exif import *


class App(ctk.CTk):
    def __init__(self, file):
        super().__init__()
        self.title("Exif Editor")
        self.minsize(540, 300)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.scroll = ctk.CTkScrollableFrame(master=self, corner_radius=0)
        self.scroll.grid(row=0, column=0, sticky='nsew')
        self.scroll.frame = ctk.CTkFrame(master=self.scroll)
        self.scroll.frame.pack()

        self.image = Image(file)
        self.fields_modified = {}

        type_map = {'orientation': lambda x: Orientation[x.split('.')[1]],
                    'resolution_unit': lambda x: ResolutionUnit[x.split('.')[1]],
                    'exposure_program': lambda x: ExposureProgram[x.split('.')[1]],
                    'exposure_mode': lambda x: ExposureMode[x.split('.')[1]],
                    'metering_mode': lambda x: MeteringMode[x.split('.')[1]],
                    'color_space': lambda x: ColorSpace[x.split('.')[1]],
                    'sensing_method': lambda x: SensingMethod[x.split('.')[1]],
                    'gps_altitude_ref': lambda x: GpsAltitudeRef[x.split('.')[1]],
                    'light_source': lambda x: LightSource[x.split('.')[1]],
                    'saturation': lambda x: Saturation[x.split('.')[1]],
                    'scene_capture_type': lambda x: SceneCaptureType[x.split('.')[1]],
                    'sharpness': lambda x: Sharpness[x.split('.')[1]],
                    'white_balance': lambda x: WhiteBalance[x.split('.')[1]],
                    'gps_latitude': lambda x: tuple(float(y) for y in x.split(' ')),
                    'gps_longitude': lambda x: tuple(float(y) for y in x.split(' ')),
                    'gps_timestamp': lambda x: tuple(float(y) for y in x.split(' ')),
                    'subsec_time': str,
                    'subsec_time_original': str,
                    'subsec_time_digitized': str}

        def save_changes():
            for (k, v) in {k.get('1.0', END).strip(): v.get('1.0', END).strip()
                           for (k, v) in self.fields_modified.items()}.items():

                if k in type_map:
                    print((k, type_map[k](v)))
                    self.image[k] = type_map[k](v)
                else:
                    try:
                        print((k, int(v)))
                        self.image[k] = int(v)
                    except ValueError:
                        print((k, v))
                        self.image[k] = v

            fd.asksaveasfile(mode='wb').write(self.image.get_file())

        frame = ctk.CTkFrame(master=self.scroll.frame)
        ctk.CTkButton(master=frame,
                      text='Add Attribute',
                      width=270
                      ).pack(side=LEFT)
        ctk.CTkButton(master=frame,
                      text='Save Changes',
                      width=270,
                      command=save_changes
                      ).pack(side=LEFT)
        frame.pack()

        for tag in self.image.list_all():
            if self.image.get(tag) and tag not in ('exif_version', 'flash'):
                frame = ctk.CTkFrame(master=self.scroll.frame)
                attr = ctk.CTkTextbox(master=frame,
                                      undo=True,
                                      height=50)
                attr.insert(END, tag)
                attr.pack(side=LEFT)

                value = ctk.CTkTextbox(master=frame,
                                       undo=True,
                                       height=50)
                value.insert(END, self.image.get(tag))
                value.pack(side=LEFT)

                self.fields_modified[attr] = value

                def remove_field(frame, attr):
                    frame.destroy()
                    del self.fields_modified[attr]
                    del self.image[attr.get('1.0', END).strip()]

                ctk.CTkButton(master=frame,
                              height=50,
                              text='Delete',
                              command=partial(remove_field, frame, attr)
                              ).pack(side=LEFT)
                frame.pack()


if __name__ == '__main__':
    App(fd.askopenfile(mode='rb')).mainloop()
