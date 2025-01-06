from flask import Flask, render_template, request, redirect, url_for
import configparser
import os, sys
import webbrowser

def determina_path_ini():
    """Determiniamo il path giusto per il file delle risorse."""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    else:
        application_path = os.getcwd()
    return application_path


app = Flask(__name__, template_folder="./risorse")
application_path = determina_path_ini()
config_name = '\\risorse\\variabili.ini'
config_path = application_path + config_name  # Specifica il percorso del file .ini

# Funzione per caricare il file .ini
def load_config():
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

# Funzione per salvare il file .ini con la gestione separata dei valori di DEFAULT
def save_config(config):
    clean_config = configparser.ConfigParser()

    # Aggiungi la sezione [DEFAULT] se esistono valori in essa
    if config.defaults():
        clean_config["DEFAULT"] = config.defaults()

    # Copia le altre sezioni senza propagare i valori di [DEFAULT]
    for section in config.sections():
        clean_config.add_section(section)
        for key, value in config.items(section, raw=True):  # raw=True evita l'espansione dei valori
            clean_config.set(section, key, value)

    # Salva il file pulito
    with open(config_path, "w") as configfile:
        clean_config.write(configfile)

@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    config = load_config()

    if request.method == "POST":
        # Aggiorna i valori nel file .ini
        for section in config.sections():
            for key in config[section]:
                if not(key in config.defaults()):
                    form_key = f"{section}.{key}"
                    if form_key in request.form:
                        value = request.form[form_key]
                        # Esegui una validazione per i campi numerici
                        if key in ["attesa_per_caricamento", "tempo_singola_ricerca"]:
                            if not value.isdigit():
                                value = "0"  # Impostiamo un valore di default se il valore non è valido
                        # Esegui una validazione per i campi booleani
                        elif key in ["headless", "driverPath"]:
                            if value not in ["True", "False"]:
                                value = "False"  # Impostiamo un valore di default se il valore non è valido
                        # Esegui una validazione per il campo browser
                        elif key == "browser" and value not in ["Edge", "Chrome"]:
                            value = "Edge"  # Impostiamo un valore di default se il valore non è valido
                        print(f"Scrittura: config[{section}][{key}] = {value}")
                        config[section][key] = value

        # Gestisci i valori della sezione [DEFAULT] in modo separato
        if config.defaults():
            for key in config.defaults():
                form_key = f"DEFAULT.{key}"
                if form_key in request.form:
                    config.set("DEFAULT", key, request.form[form_key])

        # Salva il file con cleaning
        save_config(config)
        return redirect(url_for("index"))

    # Prepara un dizionario senza propagazione dei valori di DEFAULT
    clean_config = {section: dict(config.items(section)) for section in config.sections()}

    # Rimuovi le chiavi della sezione DEFAULT da ogni sezione
    if config.defaults():
        default_keys = config.defaults().keys()
        for section in clean_config:
            clean_config[section] = {key: value for key, value in clean_config[section].items() if key not in default_keys}

    # Includi anche la sezione [DEFAULT] per l'interfaccia
    if config.defaults():
        clean_config["DEFAULT"] = dict(config.defaults())

    return render_template("input_var.html", config=clean_config)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    os._exit(0)  # Termina immediatamente il processo Python
    return "Server chiuso con successo!"  # Questo non verrà eseguito


if __name__ == "__main__":
    # Ottieni l'indirizzo del server Flask
    host = "127.0.0.1"  # Cambia con "0.0.0.0" se necessario
    port = 5000         # Cambia con un'altra porta se necessario
    url = f"http://{host}:{port}/"

    # Apri il browser predefinito al link del server Flask
    webbrowser.open(url)

    # Avvia il server Flask
    app.run(host=host, port=port, debug=True)