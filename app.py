import tkinter
import tkinter.messagebox
import customtkinter


#####################HOT RELOAD
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#################################################

################################HOT RELOAD JUST FOR DEV

# Remplacez "mon_application.py" par le nom de votre fichier principal
MAIN_SCRIPT = "app.py"

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print("Modification détectée. Rechargement de l'application...")
            os.execv(sys.executable, ["python", MAIN_SCRIPT])

##################################################################

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("TMTC GUI")

        self.wm_iconbitmap("images/hemeria.ico")

        self.geometry(f"{1100}x{580}")

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

        #settings on the sidebar

        #mode selection
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")

        #scale selection
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        self.scaling_optionemenu.set("100%")

        #TABVIEW TC OR TM

        # create tabview
        self.tabviewTMTC = customtkinter.CTkTabview(self)
        self.tabviewTMTC.grid(row=0, rowspan=3, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabviewTMTC.add("Last TC sent")
        self.tabviewTMTC.add("Last TM received")

        self.tabviewTMTC.tab("Last TC sent").grid(rowspan=3, sticky="ns")
        self.tabviewTMTC.tab("Last TC sent").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs

        self.tabviewTMTC.tab("Last TM received").grid_columnconfigure(0, weight=1)

        buffer_tc = [0x22, 0x23, 0x46, 0x67, 0x78, 0x67, 0x78, 0x67, 0x78, 0x67, 0x78, 0x67, 0x78, 0x67, 0x78, 0x67, 0x78, 0x67, 0x78, 0x67, 0x78, 0x67, 0x78]

        if(len(buffer_tc) == 0):
             #todo : protection if unavailable
            self.label_tab_1 = customtkinter.CTkLabel(self.tabviewTMTC.tab("Last TC sent"), text="No TC RECEIVE")
            self.label_tab_1.grid(row=0, column=0, padx=20, pady=20)
        else:    
            #We create the buffer frame
            self.buffer_tc = customtkinter.CTkScrollableFrame(self.tabviewTMTC.tab("Last TC sent"))
            self.buffer_tc.grid(row=0, rowspan=2, column=0, padx=0, pady=0, sticky="ns")

            result_string=""
            for i in range(len(buffer_tc)):
                result_string += f"Élément {i + 1}:                          {buffer_tc[i]}\n"
            
            self.label_tab_i = customtkinter.CTkLabel(self.buffer_tc, text=result_string)
            self.label_tab_i.grid(row=i, column=0, padx=(5, 5), pady=0)
        
        #todo : protection if unavailable
        self.label_tab_2 = customtkinter.CTkLabel(self.tabviewTMTC.tab("Last TM received"), text="TM RECEIVE")
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
        text_label = customtkinter.CTkLabel(self.TC, text="Choose a template TC :")
        text_label.grid(row=0, column=0, padx=(30, 0), pady=(0, 0))

        ######ICI boucle en fonction du service
        valuesTemplates = ["Option1", "Option2","Option3","Option4",]

        self.label_template = customtkinter.CTkOptionMenu(self.TC, dynamic_resizing=False, values=valuesTemplates)
        self.label_template.grid(row=0, column=1, padx=(20, 0), pady=(0, 0))
         
        self.template_button = customtkinter.CTkButton(self.TC, text="Send this template", command=self.open_input_dialog_event)
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

        ######ICI boucle en fonction du service
        valuesTemplates = ["Option1", "Option2","Option3","Option4",]
         
        self.template_button = customtkinter.CTkButton(self.TC_CUSTOM, text="Write custom TC", command=self.get_user_input)
        self.template_button.grid(row=0, column=1, padx=(50, 0), pady=(0, 0))

        global g_state
        g_state = self.change_state("S185")

    def open_input_dialog_event(self):
        if(g_state == "S185"):
            dialog = customtkinter.CTkInputDialog(text="Type in a number:" + g_state, title="CTkInputDialog")
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
        # Create a new input dialog window
        input_dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")

        # Add three input entries to the input dialog window
        input_entry_1 = customtkinter.CTkEntry(input_dialog, placeholder_text="Zunit")
        input_entry_2 = customtkinter.CTkEntry(input_dialog)
        input_entry_3 = customtkinter.CTkEntry(input_dialog)

        # Pack the input entries into the input dialog window
        input_entry_1.pack()
        input_entry_2.pack()
        input_entry_3.pack()

        # Add a submit button to the input dialog window
        submit_button = customtkinter.CTkButton(input_dialog, text="Submit", command=test)
        submit_button.pack()

        # Display the input dialog window
        input_dialog.mainloop()

    def test(self):
        print("hudhhd")

        

##############HOT RELOAD

if __name__ == "__main__":
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
########################

#####MAIN 

#if __name__ == "__main__":
#    app = App()
#    app.mainloop()
