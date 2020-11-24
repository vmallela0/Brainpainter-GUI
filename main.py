import docker
import os
import subprocess
from tkinter import *
from tkinter.filedialog import askopenfile
from tkinter.filedialog import askdirectory
from tkinter.colorchooser import askcolor
from tkinter.ttk import *

root = Tk()
root.title("Brainpainter")
icon = os.path.abspath(os.getcwd()) + "/cort.png" # app logo
icon_tk = PhotoImage(file = icon)
root.iconphoto(False, icon_tk)


# setting up docker connection
try:
    client = docker.from_env()
    docker_connection_status = True
    docker_status = Label(root, text = str("Docker connected!"))
    docker_status.config(font =("Helvicta", 14))
    docker_status.grid(row = 0, column = 0, sticky = W, pady = 2, padx = 2)
    container = client.containers.create("mrazvan22/brain-coloring-v2",
                                        # name='brainpainter-v2',
                                        tty = True, # keep alive
                                        auto_remove=True) # remove container for reuse
except:
    # when docker daemon isn't running
    docker_connection_status = False
    docker_status = Label(root, text = str("Docker not connected!"))
    docker_status.config(font =("Helvicta", 12))
    docker_status.grid(row = 0, column = 0, sticky = W, pady = 2, padx = 2)


def cpDocker(source, destination): # copy and paste for docker
    return (f'''docker cp {source} {str(container.short_id)}{destination}''')

def cpLocal(source, destination): # copy and paste for docker
    return(f'''docker cp {container.short_id}{source} {destination}''')

def sedDocker(setting_old, setting_new, line_number): # changes config.py on docker side
    return(f'''docker exec -it {container.id} sed -i "{line_number} s|{setting_old}|{setting_new}|" /home/brain-coloring/config.py''')

def convert_2_bpmodes(angle, mode):
    # add the view/angle config.py information

    if angle == 'Top':
        return sedDocker("IMG_TYPE = 'cortical-outer-right-hemisphere'", "IMG_TYPE = 'top'", 15)
    elif angle == 'Bottom':
        return sedDocker("IMG_TYPE = 'cortical-outer-right-hemisphere'", "IMG_TYPE = 'bottom'", 15)
    elif mode == 'Cortical-Outer':
        if 'Right-Hemisphere' == angle:
            return sedDocker("IMG_TYPE = 'cortical-outer-right-hemisphere'", "IMG_TYPE = 'cortical-outer-right-hemisphere'", 15)
        elif 'Left-Hemisphere' == angle:
            return sedDocker("IMG_TYPE = 'cortical-outer-right-hemisphere'", "IMG_TYPE = 'cortical-outer-left-hemisphere'", 15)
    elif mode == 'Cortical-Inner':
        if 'Right-Hemisphere' == angle:
            return sedDocker("IMG_TYPE = 'cortical-outer-right-hemisphere'", "IMG_TYPE = 'cortical-inner-right-hemisphere'", 15)
        elif 'Left-Hemisphere' == angle:
            return sedDocker("IMG_TYPE = 'cortical-outer-right-hemisphere'", "IMG_TYPE = 'cortical-inner-left-hemisphere'", 15)
    elif mode == 'Subcortical':
        return sedDocker("IMG_TYPE = 'cortical-outer-right-hemisphere'", "IMG_TYPE = 'subcortical'", 15)

class Gui:
    def open_file(self, print_row_number):
        file = askopenfile(mode ='r', filetypes =[('CSV Files', '*.csv')])
        if file is not None:
            # print(file)
            dataInput = file.name
            self.dataInput = dataInput
            dataInputLabel = Label(root, text = str(dataInput))
            dataInputLabel.config(font =("Helvicta", 14))
            dataInputLabel.grid(row = print_row_number, column = 1, sticky = W, pady = 2, padx = 2)
        else:
            dataInputLabel = Label(root, text = "File could not be opened")
            dataInputLabel.config(font =("Helvicta", 14))
            dataInputLabel.grid(row = print_row_number, column = 1, sticky = W, pady = 2, padx = 2)

    def get_folder_dir(self, row_number):
        file = askdirectory()
        if file is not None:
            # print(file)
            dataOutput = file
            self.dataOutput = dataOutput
            dataOutputLabel = Label(root, text = str(dataOutput))
            dataOutputLabel.config(font =("Helvicta", 14))
            dataOutputLabel.grid(row = row_number, column = 1, sticky = W, pady = 2)
        else:
            dataOutputLabel = Label(root, text = "File could not be opened")
            dataOutputLabel.config(font =("Helvicta", 14))
            dataOutputLabel.grid(row = row_number, column = 1, sticky = W, pady = 2, padx = 2)

    def choose_color(self, val, display, grid_num):
        # variable to store hexadecimal code of color
        result = askcolor(title = "Color Chooser")
        blender_color_value = [color/256 for color in result[0]]
        print(blender_color_value)
        display = Label(root, text = str(blender_color_value))
        display.grid(row = grid_num, column = 1, sticky = W, pady = 2)
        self.colors[val] = blender_color_value

    def __init__(self, instance_name):
        self.name = instance_name
        self.dataInput = ''
        self.dataOutput = ''
        self.colors = [[1,1,1], [1,1,0], [1,0.4,0], [1,0,0]]

    def run(self):
        menubar = Menu(root)

        # output folder name
        output_folder = Menu(menubar, tearoff=0)
        output_folder = Entry(root, textvariable = "Output",font=('Helvicta',14))
        output_folder.insert(0, "Brainpainter_output")
        output_folder.grid(row = 1, column = 1, sticky = W, pady = 2)

        output_folder_label = Label(root, text = "Output folder name:")
        output_folder_label.grid(row = 1, column = 0, sticky = W, pady = 2)

        # setting up input file picker
        input_file = Menu(menubar, tearoff=0)
        input_file = Button(root, text ='Pick input data', command = lambda:self.open_file(3))
        input_file.grid(row = 2, column = 1, sticky = W, pady = 2, padx = 2)

        input_file_label = Label(root, text = "Choose input file:")
        input_file_label.grid(row = 2, column = 0, sticky = W, pady = 2)

        # setting up output file picker
        output_file = Menu(menubar, tearoff=0)
        output_file = Button(root, text ='Pick output folder', command = lambda:self.get_folder_dir(5))
        output_file.grid(row = 4, column = 1, sticky = W, pady = 2, padx = 2)

        output_file_label = Label(root, text = "Choose output location:")
        output_file_label.grid(row = 4, column = 0, sticky = W, pady = 2)

        #! getting config preferences
        # type
        brain_types = ["'pial'", "'pial'", "'inflated'", "'white'",]
        brain_type = StringVar(root)
        brain_type.set(brain_types[0])
        brain_type_chooser = OptionMenu(root, brain_type, *brain_types)
        brain_type_chooser.grid(row = 6, column = 1, sticky = W, pady = 2, padx = 2)

        brain_type_chooser_label = Label(root, text = "Choose brain type:")
        brain_type_chooser_label.grid(row = 6, column = 0, sticky = W, pady = 2)

        # atlas selection
        atlas_options = ["'DK'", "'DK'", "'Destrieux'", "'Tourville'"]
        atlas = StringVar(root)
        atlas.set(atlas_options[0])
        atlas_chooser = OptionMenu(root, atlas, *atlas_options)
        atlas_chooser.grid(row = 7, column = 1, sticky = W, pady = 2)

        atlas_chooser_label = Label(root, text = "Choose atlas:")
        atlas_chooser_label.grid(row = 7, column = 0, sticky = W, pady = 2)

        # image type
        img_angles = ['Right-Hemisphere', 'Right-Hemisphere', 'Left-Hemisphere', 'Top', 'Bottom']
        img_angle = StringVar(root)
        img_angle.set(img_angles[0])
        img_angle_chooser = OptionMenu(root, img_angle, *img_angles)
        img_angle_chooser.grid(row = 8, column = 1, sticky = W, pady = 2)

        img_angle_chooser_label = Label(root, text = "Choose angle:")
        img_angle_chooser_label.grid(row = 8, column = 0, sticky = W, pady = 2)

        # modes
        modes = ['Cortical-Outer', 'Cortical-Outer', 'Cortical-Inner', 'Subcortical']
        mode = StringVar(root)
        mode.set(modes[0])
        mode_chooser = OptionMenu(root, mode, *modes)
        mode_chooser.grid(row = 9, column = 1, sticky = W, pady = 2)

        mode_chooser_label = Label(root, text = "Choose mode:")
        mode_chooser_label.grid(row = 9, column = 0, sticky = W, pady = 2)

        # color picker

        # c0
        color_0 = Menu(menubar, tearoff=0)
        color_0 = Button(root, text ='Pick color 0', command = lambda:self.choose_color(0, color_0_display, 11))
        color_0.grid(row = 10, column = 1, sticky = W, pady = 2, padx = 2)

        color_0_label = Label(root, text = "Choose biomarker value 0:")
        color_0_label.grid(row = 10, column = 0, sticky = W, pady = 2)

        color_0_display = Label(root, text = str(self.colors[0]))
        color_0_display.grid(row = 11, column = 1, sticky = W, pady = 2)

        # c1
        color_1 = Menu(menubar, tearoff=0)
        color_1 = Button(root, text ='Pick color 1', command = lambda:self.choose_color(1, color_1_display, 13))
        color_1.grid(row = 12, column = 1, sticky = W, pady = 2, padx = 2)

        color_1_label = Label(root, text = "Choose biomarker value 1:")
        color_1_label.grid(row = 12, column = 0, sticky = W, pady = 2)

        color_1_display = Label(root, text = str(self.colors[1]))
        color_1_display.grid(row = 13, column = 1, sticky = W, pady = 2)

        # c2
        color_2 = Menu(menubar, tearoff=0)
        color_2 = Button(root, text ='Pick color 2', command = lambda:self.choose_color(2, color_2_display, 15))
        color_2.grid(row = 14, column = 1, sticky = W, pady = 2, padx = 2)

        color_2_label = Label(root, text = "Choose biomarker value 2:")
        color_2_label.grid(row = 14, column = 0, sticky = W, pady = 2)

        color_2_display = Label(root, text = str(self.colors[2]))
        color_2_display.grid(row = 15, column = 1, sticky = W, pady = 2)

        # c3
        color_3 = Menu(menubar, tearoff=0)
        color_3 = Button(root, text ='Pick color 3', command = lambda:self.choose_color(3, color_3_display, 17))
        color_3.grid(row = 16, column = 1, sticky = W, pady = 2, padx = 2)

        color_3_label = Label(root, text = "Choose biomarker value 3:")
        color_3_label.grid(row = 16, column = 0, sticky = W, pady = 2)

        color_3_display = Label(root, text = str(self.colors[3]))
        color_3_display.grid(row = 17, column = 1, sticky = W, pady = 2)

        # resolution
        resolution = Menu(menubar, tearoff=0)
        resolution = Entry(root, textvariable = "Resolution",font=('Helvicta',14))
        resolution.insert(0, "1200,900")
        resolution.grid(row = 18, column = 1, sticky = W, pady = 2)

        resolution_label = Label(root, text = "Resolution:")
        resolution_label.grid(row = 18, column = 0, sticky = W, pady = 2)

        # run button
        run = Menu(menubar, tearoff=0)
        run = Button(root, text="Run Brainpainter", command = lambda: self.run_docker(self.dataInput, self.dataOutput, output_folder.get(), brain_type.get(), atlas.get(), img_angle.get(), mode.get(), self.colors, resolution.get()))
        run.grid(row = 20, column = 1, sticky = W, pady = 2, padx = 2)

    def run_docker(self, input_location, output_location, output_name, brain_type, atlas, img_angle, mode, colors, resolution):
        try:
            container.start()
            # os.system('docker ps --no-trunc')
            # os.system("docker ps") # running docker conatiners

            INPUT_DOCKER = ':/home/brain-coloring/input'
            input_file_name = os.path.basename(input_location)
            cmdCopy = cpDocker(input_location, INPUT_DOCKER)


            cmdRun = f'''docker exec -it {container.id} make -C /home/brain-coloring/'''

            OUTPUT_DOCKER = ':/home/brain-coloring/output/' + output_name
            cmdExtract = cpLocal(OUTPUT_DOCKER, output_location)

            print(cmdCopy)
            subprocess.Popen(cmdCopy, shell=True).wait() # copying inputs into docker container


            print(sedDocker('DK_template.csv', input_file_name, 2)) # changes input location in docker
            subprocess.Popen(sedDocker('DK_template.csv', input_file_name, 2), shell=True).wait()

            print(sedDocker("OUTPUT_FOLDER = 'output/DK_Output'","OUTPUT_FOLDER = 'output/" + output_name + "'", 4)) # changes output location in docker
            subprocess.Popen(sedDocker("OUTPUT_FOLDER = 'output/DK_Output'","OUTPUT_FOLDER = 'output/" + output_name + "'", 4), shell=True).wait()

            # changing config settings
            print(sedDocker("ATLAS = 'DK'", "ATLAS = " + atlas, 7)) # atlas settings
            subprocess.Popen(sedDocker("ATLAS = 'DK'", "ATLAS = " + atlas, 7), shell=True).wait()

            print(sedDocker("BRAIN_TYPE = 'pial'", "BRAIN_TYPE = " + brain_type, 10)) # brain_type settings
            os.system(sedDocker("BRAIN_TYPE = 'pial'", "BRAIN_TYPE = " + brain_type, 10))

            print(convert_2_bpmodes(img_angle, mode))
            os.system(convert_2_bpmodes(img_angle, mode)) # changing the mode/angle

            print(sedDocker("# default is white", "COLORS_RGB = " + str(colors), 29))
            os.system(sedDocker("# default is white", "COLORS_RGB = " + str(colors), 29)) # changing colors
            
            print(sedDocker("RESOLUTION = (1200, 900)", "RESOLUTION = (" + resolution + ")", 27))
            os.system(sedDocker("RESOLUTION = (1200, 900)", "RESOLUTION = (" + resolution + ")", 27))

            print(cmdRun)
            subprocess.Popen(cmdRun, shell=True).wait() # generating images

            print(cmdExtract)
            subprocess.Popen(cmdExtract, shell=True).wait() # moving images from docker to local

            mode_chooser_label = Label(root, text = "Images generated")
            mode_chooser_label.grid(row = 21, column = 1, sticky = W, pady = 2, padx = 2)
        except:
            print("raised")
            mode_chooser_label = Label(root, text = "Oops! Something went wrong. Make sure you filled out the values")
            mode_chooser_label.grid(row = 21, column = 1, sticky = W, pady = 2, padx = 2)

if __name__ == "__main__":
    # tkinter init
    gui = Gui("main")
    gui.run()
    mainloop()
    container.stop() # kills container for reuse
