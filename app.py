
import os
import sys
import tkinter
from tkinter import StringVar
import tkinter.messagebox
import customtkinter

from PIL import Image, ImageTk

import threading
import time

import socket
import datetime

#####################HOT RELOAD
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

sys.path.append("/opt/ets.backup/python/lib/python3.10/site-packages/")

from ets.pus.yoda.specifics.pus185 import TC185_150

#################################################

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

###########################################
############SEND AND RECEIVE SECTION#######
###########################################

def create_tc_185_150(nameCommand, Zunit, askTM, timeout, nbCmd, commande):

    #We get the value
    tc = TC185_150()
    tc.dgene_ar_zunit = Zunit
    tc.dgene_ar_zasktm = askTM
    tc.dgene_ar_dtimeout = timeout
    tc.dgene_ar_ncmd = nbCmd

    #Transform the command 
    for i in range(len(commande)):
        tc.dgene_ar_rcmd[i] = commande[i]

    tc.encode()

    #Service classic header
    message = b'\xeb\x90\x20\x09\x06\x7b\x00\xff\x00\x00\x00\x00\x00\x00'

    #Send UDP MESSAGE
    receiveMessage = send_udp_message("127.0.0.1", 14567, message+tc._buffer)

    #We will add this in the tc file 
    output_file = "reception/tc.txt"
    data = message+tc._buffer
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    formatted_data = ", ".join([f"0x{byte:02X}" for byte in data])
    message = f"{nameCommand} {current_time} [{formatted_data}]"
    # Write in the file
    with open(output_file, "a") as file:
        file.write(message + "\n")

def send_udp_message(host, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((host, port))
    sock.sendall(message)

def thread_tm():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 14568

    # create udp socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    output_file = "reception/tm.txt"

    i = 0
    try:
        while True:
            data, addr = sock.recvfrom(1024)  # Réception du message UDP
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_data = ", ".join([f"0x{byte:02X}" for byte in data])
            message = f"TM_{i} {current_time} [{formatted_data}]"
            i += 1
            # Écrire le message dans le fichier
            with open(output_file, "a") as file:
                file.write(message + "\n")

    except KeyboardInterrupt:
        print("UDP server was stoped.")
    finally:
        sock.close()

def read_template_s185_file(filename):
    resultat = []
    with open(filename, 'r') as file:
        for ligne in file:
            elements = ligne.strip().split()
            if len(elements) >= 6:
                tc185_info = {
                    "name": elements[0],
                    "equipment": elements[1],
                    "timeout": elements[2],
                    "n_cmd": elements[3],
                    "r_cmd": elements[4],
                }
                resultat.append(tc185_info)
    return resultat

def display_template(self, last_state, ctkTemplateList):
    global g_state

    #Penser a supprimer tous les objets si on change d'état
    if(g_state != last_state):
        if(g_state == "S185" or g_state == None):
            resultat = read_template_s185_file("templates/S185.txt")
            valuesTemplates = {tc['name']: tc for tc in resultat}
            # Créez le menu déroulant en utilisant le dictionnaire valuesTemplates
            self.label_template = customtkinter.CTkOptionMenu(ctkTemplateList, dynamic_resizing=False, values=list(valuesTemplates.keys()))
            self.label_template.grid(row=0, column=0, padx=(10, 0), pady=(0, 0), columnspan=2, sticky="ew")


    self.after(1000, lambda :display_template(self, g_state, ctkTemplateList))
    
def display_tc(self, last_list):
    global buffer_tc

    # First, verify if the list is the same as before
    if buffer_tc != last_list:
        # Clear the existing Text widget
        self.buffer_tc.delete("1.0", "end")

        # Create a table string to hold the new content
        table = ""
        for i in range(len(buffer_tc)):
            hex_value = hex(buffer_tc[i])
            table += f"Index {i}:\t\t\t{hex_value}\n"

        # Update the Text widget with the new content
        self.buffer_tc.insert("1.0", table)

    self.after(500, lambda buffer_tc=buffer_tc: display_tc(self, buffer_tc))

def display_tmtc_first_word(file_path, ctkframe, nb_lines, self):

    # EYE LOGO
    image_pil = Image.open("images/eye.png")
    image_customtkinter = customtkinter.CTkImage(image_pil)

    with open(file_path, 'r') as file:
        lines = file.readlines()
        nb_lines_now = len(lines)
    
    if nb_lines != nb_lines_now:
        if nb_lines_now > 0:
            last_line = lines[-1]  # Get the file last
            words = last_line.split()
            if words:
                first_word = words[0]
                date = words[1]

                item_value_label = customtkinter.CTkLabel(ctkframe, text=f"{first_word}")
                item_value_label.grid(row=(len(lines)-1), column=0, padx=(5, 5), pady=2, sticky="w")

                if file_path == "reception/tc.txt":
                    button_print = customtkinter.CTkButton(ctkframe, image=image_customtkinter, text="", width=0, command=lambda: self.change_print_tmtc("TC", (len(lines)-1)))
                else:
                    button_print = customtkinter.CTkButton(ctkframe, image=image_customtkinter, text="", width=0, command=lambda: self.change_print_tmtc("TM", (len(lines)-1)))
                
                button_print.grid(row=(len(lines)-1), column=2, padx=(0, 5), pady=2, sticky="e")

                ctkframe.columnconfigure(2, weight=1)
    
    self.after(1000, lambda: display_tmtc_first_word(file_path, ctkframe, nb_lines_now, self))

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.init_app()

        #We flush the differents files
        with open("reception/tc.txt", 'w') as fichier:
            fichier.truncate(0)

        with open("reception/tm.txt", 'w') as fichier:
            fichier.truncate(0)

        #we launch the tm reception server thread
        tmThread = threading.Thread(target=thread_tm) 

        tmThread.start()

        self.after(0, lambda:display_tmtc_first_word("reception/tc.txt", self.tc_list, 0, self))
        self.after(1000, lambda:display_tmtc_first_word("reception/tm.txt", self.tm_list, 0, self))
        self.after(0, lambda:display_tc(self, []))
        self.after(0, lambda :display_template(self, 0, self.TC))

        global g_state
        g_state = self.change_state("S185")
        
        global g_tmtc
        g_tmtc = ["TC", 0]

    def init_app(self):

         # configure window
        self.title("TMTC GUI")

        #configure logo
        img = tkinter.PhotoImage(file="images/hemeria.png")
        self.tk.call('wm', 'iconphoto', self._w, img)

        #configure size of windows
        self.state("normal")

        # configure grid layout (4x4)
        self.grid_columnconfigure((1,2), weight=2)
        self.grid_columnconfigure(3, weight=1)

        self.grid_rowconfigure((2,3), weight=1)
        self.grid_rowconfigure((0, 1), weight=2)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        #title of the sidebar
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Service", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        ###########################################################
        ########################SERVICE BUTTON#####################
        ###########################################################

        #button of the sidebar

        #button 1
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=lambda: self.change_state("S17"), text="Service 17")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        #button 2
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=lambda: self.change_state("S185"), text="Service 185")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        #button3
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=lambda: self.change_state("S3"), text="Service 3")
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        ###########################################################
        #######################SETTINGS BUTTON#####################
        ###########################################################

        #settings on the sidebar

        #mode selection
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")

        #scale selection
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"], command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        self.scaling_optionemenu.set("100%")


        # create tabview
        self.tabviewLISTTMTC = customtkinter.CTkTabview(self)
        self.tabviewLISTTMTC.grid(row=0, rowspan=3, column=2, padx=(5, 0), pady=(20, 0), sticky="nsew")
        self.tabviewLISTTMTC.add("Last TC sent")
        self.tabviewLISTTMTC.add("Last TM received")

        
        self.tabviewLISTTMTC.tab("Last TC sent").grid(rowspan=5, column=0, columnspan=2, sticky="nsew",)
        self.tabviewLISTTMTC.tab("Last TC sent").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabviewLISTTMTC.tab("Last TC sent").grid_rowconfigure(0, weight=1)  # configure grid of individual tabs

        self.tabviewLISTTMTC.tab("Last TM received").grid(rowspan=5, column=0, columnspan=2, sticky="nsew")
        self.tabviewLISTTMTC.tab("Last TM received").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabviewLISTTMTC.tab("Last TM received").grid_rowconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabviewLISTTMTC.tab("Last TM received").grid_remove()

        #############################################
        #####PSEUDO THREAD WHO PRINT TC SEND#########
        #############################################

        self.tc_list = customtkinter.CTkScrollableFrame(self.tabviewLISTTMTC.tab("Last TC sent"))
        self.tc_list.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        item_value_label = customtkinter.CTkLabel(self.tc_list,text="No TC sent")
        item_value_label.grid(row=0, column=0, padx=(5,5), pady=2, sticky="nsew")

        #############################################
        #####PSEUDO THREAD WHO PRINT TM SEND#########
        #############################################

        self.tm_list = customtkinter.CTkScrollableFrame(self.tabviewLISTTMTC.tab("Last TM received"))
        self.tm_list.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        #TABVIEW TC OR TM BRUT

        # create tabview
        self.tabviewTMTC = customtkinter.CTkTabview(self)
        self.tabviewTMTC.grid(row=0, rowspan=3, column=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabviewTMTC.add("BRUT")
        self.tabviewTMTC.add("DECODED")

        self.tabviewTMTC.tab("BRUT").grid(rowspan=2, column=0, sticky="nsew")
        self.tabviewTMTC.tab("BRUT").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabviewTMTC.tab("BRUT").grid_rowconfigure(0, weight=1)  # configure grid of individual tabs

        # Create Scrollable Frame
        self.buffer_tc = customtkinter.CTkTextbox(self.tabviewTMTC.tab("BRUT"))
        self.buffer_tc.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        #Default label
        self.buffer_tc.insert("0.0", "Waiting...")

        self.tabviewTMTC.tab("DECODED").grid_columnconfigure(0, weight=1)

        global buffer_tc 

        buffer_tc = []
        
        #todo : protection if unavailable
        self.label_tab_2 = customtkinter.CTkLabel(self.tabviewTMTC.tab("DECODED"), text="TM RECEIVE")
        self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)

        #SERVICE DESCRIPTION

        # create textbox, update among service
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 2)
        
        #Sending TC

        self.TC = customtkinter.CTkFrame(self)
        self.TC.grid(row=1, column=1, padx=(20,0), pady=(20,0), sticky="nsew")

        self.TC.columnconfigure((0,1,2), weight=1)
        self.TC.rowconfigure((0), weight=1)
        self.TC.rowconfigure((1,2,3), weight=0)

        #TEMPLATE TC

        self.template_button = customtkinter.CTkButton(self.TC, text="Send", command=self.send_tc_template)
        self.template_button.grid(row=0, column=2, padx=(20, 0), pady=(0, 0))

        #SPECIFIC TC

        self.TC_CUSTOM = customtkinter.CTkFrame(self)
        self.TC_CUSTOM.grid(row=2, column=1, padx=(20,0), pady=(20,0), sticky="nsew")

        self.TC_CUSTOM.columnconfigure((0,1,2), weight=1)
        self.TC_CUSTOM.rowconfigure((0), weight=1)
        self.TC_CUSTOM.rowconfigure((1,2,3), weight=0)

        #TEMPLATE TC_CUSTOM
        text_label = customtkinter.CTkLabel(self.TC_CUSTOM, text="CUSTOM A TC :")
        text_label.grid(row=0, column=0, padx=(30, 0), pady=(0, 0))
         
        self.template_button = customtkinter.CTkButton(self.TC_CUSTOM, text="Write custom TC", command=self.get_user_input)
        self.template_button.grid(row=0, column=1, padx=(50, 0), pady=(0, 0))

    def open_input_dialog_event(self):
        if(g_state == "S185"):
            dialog = customtkinter.CTkInputDialog(text="Type in a number0:" + g_state, title="CTkInputDialog")
            print("CTkInputDialog:", dialog.get_input())
            
        elif(g_state == "S17"):
            dialog = customtkinter.CTkInputDialog(text="Type in a number:" + g_state, title="CTkInputDialog")
            print("CTkInputDialog:", dialog.get_input())

        elif(g_state == "S3"):
            dialog = customtkinter.CTkInputDialog(text="Type in a number:" + g_state, title="CTkInputDialog")
            print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event1(self):
        print("sidebar_button click v1")

    def sidebar_button_event(self):
        print("sidebar_button click")

    def change_state(self, state):
        global g_state
        g_state = state
        
        #A definir générique
        if(g_state == "S185"):
            new_text = "Service185 : \n\nService permettant la gestion des équipements. Il permet à partir de l'ID d'un équipement demandé à effectuer une commande. Cette commande peut-être de type executif ou informationnelle. La TC qui compose se service possède les champs suivants :  \n\n- Zunit : ID de l'équipement que l'on souhaite envoyer une commande\n\n- askTM : On précise si l'on souhaite obtenir une réponse ou non\n\n- Timeout : Si l'équipement n'a pas répondu dans le temps imparti (en s), on lève une TM d'erreur\n\n- Commande : On décrit ici la commande que l'on souhaite envoyé"
            self.textbox.delete("0.0", customtkinter.END)  # Efface tout le texte existant dans le CTkTextbox
            self.textbox.insert("0.0", new_text)

        elif(g_state == "S17"):
            new_text = "Service17 : \n\nService permettant d'envoyer un ping."
            self.textbox.delete("0.0", customtkinter.END)  # Efface tout le texte existant dans le CTkTextbox
            self.textbox.insert("0.0", new_text)
        elif(g_state == "S3"):
            new_text = "Service3 : \n\nService non défini."
            self.textbox.delete("0.0", customtkinter.END)  # Efface tout le texte existant dans le CTkTextbox
            self.textbox.insert("0.0", new_text)

    # Définissez une fonction pour afficher la fenêtre de dialogue
    def get_user_input(self):
        # # Create a new input dialog window
        input_dialog = customtkinter.CTkInputDialog(text="SOON")

        # # Créez un cadre pour organiser les nouveaux widgets
        # new_frame = customtkinter.CTkFrame(input_dialog)

        # # Ajoutez les nouveaux widgets au cadre
        # input_entry_1 = customtkinter.CTkEntry(new_frame, placeholder_text="Zunit")
        # input_entry_2 = customtkinter.CTkEntry(new_frame, placeholder_text="Ask_TM")
        # input_entry_3 = customtkinter.CTkEntry(new_frame, placeholder_text="Timeout")
        # input_entry_4 = customtkinter.CTkEntry(new_frame, placeholder_text="N_CMD")
        # input_entry_5 = customtkinter.CTkEntry(new_frame, placeholder_text="R_CMD")
        # submit = customtkinter.CTkButton(new_frame, text="Write custom TC", command=self.submit_callback(input_dialog, input_entry_1, input_entry_2, input_entry_3, input_entry_4, input_entry_5))

        # # Organisez les widgets dans le cadre en utilisant "pack"
        # input_entry_1.pack()
        # input_entry_2.pack()
        # input_entry_3.pack()
        # input_entry_4.pack()
        # input_entry_5.pack()
        # submit.pack()

        # # Ajoutez le cadre à l'objet input_dialog en utilisant "pack" ou "grid" selon vos besoins
        # new_frame.pack()  # Ou new_frame.grid(...)

        # # Display the input dialog window
        # input_dialog.mainloop()

    def change_print_tmtc(self, type, line_number):
        global g_tmtc
        g_tmtc = [type, line_number]
        global buffer_tc

        if(type == "TC"):
            file_path = "reception/tc.txt"
        else : 
            if (type == "TM"):
                file_path = "reception/tm.txt"

        with open(file_path, 'r') as file:
            # Lisez toutes les lignes du fichier dans une liste
            lines = file.readlines()

            # Vérifiez si la ligne demandée est dans la plage valide
            if 0 <= line_number < len(lines):
                # Séparez la ligne en mots en utilisant l'espace comme séparateur
                words = lines[line_number].split()

                # Initialisez une liste pour stocker les octets
                byte_list = []

                # Parcourez les mots à partir du troisième mot (les octets)
                for word in words[2:]:
                    # Vérifiez si le mot commence par '[' (indiquant le début de la liste)
                    if word.startswith('['):
                        # Supprimez le caractère '[' du mot
                        word = word[1:]

                    # Vérifiez si le mot se termine par ']' (indiquant la fin de la liste)
                    if word.endswith(']'):
                        # Supprimez le caractère ']' du mot
                        word = word[:-1]

                    # Divisez le mot en éléments séparés par des virgules
                    byte_elements = word.split(',')

                    # Convertissez chaque élément en octet (s'il n'est pas vide) et ajoutez-le à la liste
                    for element in byte_elements:
                        element = element.strip()
                        if element:
                            byte_list.append(int(element, 0))

        buffer_tc = byte_list

    def get_command_line_s185(self, command_name):
        file_path = "templates/S185.txt"
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith(command_name):
                    # Séparez la ligne en mots en utilisant l'espace comme séparateur
                    words = line.split()
                    # Convertissez les éléments appropriés en entiers ou en chaînes
                    command_elements = [words[0]] + [int(words[i]) if i in {1, 2, 3} else words[i] for i in range(1, len(words))]
                    return command_elements
        return None  # La commande n'a pas été trouvée

    def send_tc_template(self):
        selected_option = self.label_template.get()
        tc_185_150 = self.get_command_line_s185(selected_option)

        #We transform the str to int list
        byte_data = bytes.fromhex(tc_185_150[5])
        integer_list = list(byte_data)

        create_tc_185_150(tc_185_150[0], int(tc_185_150[1]), int(tc_185_150[2]), int(tc_185_150[3]), int(tc_185_150[4]), integer_list)
    
#####MAIN 

if __name__ == "__main__":
   app = App()
   app.mainloop()
