import tkinter as tk
from PIL import Image, ImageTk
import menu
import question_editor
import json
import os
from plansza import Plansza
from pionek import Pionek, pos

def powrot_przycisk(okno):
    okno.destroy()
    menu.main()

def uruchom_okno_prowadzacy():
    if not os.path.exists("gra_status.json"):
        with open("gra_status.json", "w", encoding="utf-8") as f:
            json.dump({"status": "oczekiwanie", "gracze": []}, f)

    okno = tk.Tk()
    okno.title("Okno Prowadącego")

    screen_width = okno.winfo_screenwidth()
    screen_height = okno.winfo_screenheight()
    okno.geometry(f"{screen_width}x{screen_height}")
    okno.configure(bg="#e2dbd8")

    #powrot_img = Image.open("powrot.png").resize((210, 70))
    #powrot_photo = ImageTk.PhotoImage(powrot_img)
    powrot_button = tk.Button(okno, text="POWRÓT", command=lambda: powrot_przycisk(okno), font="Georgia 25", fg="#d9dad9", bg="#750006")
    #powrot_button.image = powrot_photo
    powrot_button.place(x=50, y=30)

    logo_img = Image.open("logo2.png").resize((800, 700))
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(okno, image=logo_photo, bg="#e2dbd8")
    logo_label.image = logo_photo
    logo_label.place(x=screen_width/2-400, y=-280)

    edytuj_button = tk.Button(
        okno,
        text="EDYTUJ BAZĘ PYTAŃ",
        command=lambda: [okno.destroy(), question_editor.uruchom_edycje()],
        bg="#750006",
        fg="#d9dad9",
        font='Georgia',
        width=20,
        height=1
    )
    edytuj_button.place(x=screen_width/2-120, y=550)

    def start_gra():
        try:
            with open("gra_status.json", "r", encoding="utf-8") as f:
                dane = json.load(f)
        except FileNotFoundError:
            dane = {}

        dane["status"] = "start"
        if "gracze" not in dane:
            dane["gracze"] = []

        with open("gra_status.json", "w", encoding="utf-8") as f:
            json.dump(dane, f, indent=2)
            

    tk.Button(okno, text="START GRY", command=start_gra, fg="#d9dad9", bg="#750006", font='Georgia', width=20, height=1).place(x=screen_width/2-120, y=450)

    def reset_gra():
        with open("gra_status.json", "w", encoding="utf-8") as f:
            json.dump({"status": "oczekiwanie", "gracze": []}, f)
        for pionek in pionki_graczy.values():
            if pionek.img_id and pionek.numerPola is not None:
                try:
                    plansza_do_gry.pola[pionek.numerPola].tlo.delete(pionek.img_id)
                except:
                    pass
        pionki_graczy.clear()

    tk.Button(okno, text="RESET GRY", command=reset_gra, fg="#d9dad9", bg="#750006", font='Georgia', width=20, height=1).place(x=screen_width/2-120, y=500)

    def on_closing():
        with open("gra_status.json", "w", encoding="utf-8") as f:
            json.dump({"status": "oczekiwanie", "gracze": []}, f)
        okno.destroy()

    okno.protocol("WM_DELETE_WINDOW", on_closing)

    ranking_header = tk.Canvas(okno, width=227, height=50, bg="#750006", highlightthickness=0)
    ranking_header.place(x=50, y=200)
    ranking_header.create_text(113, 25, text="RANKING:", fill="#d9dad9", font=('Georgia', 20, 'bold'))

    ranking_canvas = tk.Canvas(okno, width=227, height=450, bg="#750006", highlightthickness=0)
    ranking_canvas.place(x=50, y=250)

    def odswiez_ranking():
        try:
            with open("gra_status.json", "r", encoding="utf-8") as f:
                dane = json.load(f)
            gracze = sorted(dane.get("gracze", []), key=lambda x: -x["ects"])
            ranking_canvas.delete("all")
            for idx, g in enumerate(gracze):
                ranking_canvas.create_text(
                    113, 20 + idx * 30,
                    text=f"{g['login']}:  {g['ects']}",
                    fill="white",
                    font=("Arial", 14)
                )
        except Exception as e:
            print(f"[Błąd odświeżania rankingu]: {e}")

        okno.after(1000, odswiez_ranking)
    pole_x = int(screen_width/15)
    pole_y=int(screen_height/14)
    dl_planszy=11
    szer_planszy=8
    margin_left=screen_width/2-(szer_planszy/2+1)*pole_x
    margin_top = screen_height / 2 - (dl_planszy / 2) * pole_y

    plansza_do_gry = Plansza(okno, dl_planszy, szer_planszy, margin_top, margin_left, pole_x, pole_y)
    plansza_do_gry.WypelnijDomyslnie()
    plansza_do_gry.Rysuj()

    pionki_graczy = {}

    def odswiez_pionki():
        try:
            with open("gra_status.json", "r", encoding="utf-8") as f:
                dane = json.load(f)

            for g in dane.get("gracze", []):
                login = g["login"]
                kolor = g["kolor"]
                ksztalt = g.get("ksztalt", 0)  # domyślnie 0
                pole = g.get("pole", 0)

                if login not in pionki_graczy:
                    pionek = Pionek(kolor, ksztalt)
                    pionek.numerPola = pole
                    pionki_graczy[login] = pionek
                else:
                    pionek = pionki_graczy[login]
                    stare_pole = pionek.numerPola
                    if pionek.img_id is not None:
                        plansza_do_gry.pola[stare_pole].tlo.delete(pionek.img_id)
                    pionek.numerPola = pole
                    pionek.kolor = kolor
                    pionek.ksztalt = ksztalt

                # Prawidłowe wyświetlenie wybranego pionka
                img = pionek.get_image(plansza_do_gry.pola[pole].tlo)
                pionek.img_id = plansza_do_gry.pola[pole].tlo.create_image(
                    12 + pos[kolor][0],
                    18 + pos[kolor][1],
                    image=img
                )
        except Exception as e:
            print(f"[Błąd odświeżania pionków]: {e}")

        okno.after(1000, odswiez_pionki)

    odswiez_ranking()
    odswiez_pionki()

    okno.mainloop()
