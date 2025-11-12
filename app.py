from flask import Flask, render_template, request, send_file
import pandas as pd
from io import BytesIO
import os
import zipfile

app = Flask(__name__)

# Ingrédients par personne pour chaque recette
ingredients = {
    "Ratatouille semoule": {
        "Poivrons rouges (unités)": 0.25,
        "Poivrons jaunes (unités)": 0.25,
        "Oignons (unités)": 0.125,
        "Ail (gousses)": 0.25,
        "Herbes de Provence (g)": 1,
        "Tomates (unités)": 0.5,
        "Courgettes (unités)": 0.25,
        "Aubergines (unités)": 0.25,
        "Semoule (g)": 90,
        "Huile d'olive (cl)": 2
    },
    "Risotto champignons": {
        "Riz à risotto (g)": 60,
        "Champignons de Paris (g)": 70,
        "Oignon (unités)": 0.5,
        "Ail (gousses)": 0.5,
        "Bouillon de légumes ou de volaille (cl)": 250,
        "Huile d'olive (cl)": 10,
        "Parmesan (g)": 20
    },

    "Riz poulet curry" : {
        "Riz basmati ou thaï (g)": 60,
        "Filet de Blanc de Poulet (filets)": 1.5,
        "Crème liquide (cl)": 20,
        "Oignon (unités)": 0.5,
        "Ail (gousses)": 0.5,
        "Poivron jaune ou rouge (unités)": 0.5,
        "Huile d'olive (cl)": 2,
        "Curcuma (g)": 1,
        "Curry (g)": 2
        },

    "Pates aux legumes" : {
        "Pâtes (g)": 90,
        "Courgette (unités)": 0.25,
        "Poivron rouge (unités)": 0.25,
        "Oignon (unités)": 0.25,
        "Tomates concassées (cl)": 10,
        "Huile d'olive (cl)": 2,
        "Herbes de Provence (g)": 1,
        },

    "Spaghetti carbonara" : {
        "Spaghetti (g)": 100,  
        "Lardons fumés (g)": 50,
        "Crème liquide (cl)": 20,
        "Parmesan râpé (g)": 15,
        }
}

# Catégories de mangeurs et leur coefficient
coefficients = {
    "orange": 0.6,
    "bleu_fille": 0.8,
    "bleu_garcon": 1.0,
    "rouge_fille": 1.0,
    "rouge_garcon": 1.2,
    "cheffe": 1.0,
    "chef": 1.2,
    "maxi_gros_mangeur": 1.5
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form')
def form():
    recette = request.args.get("recette")
    return render_template('form.html', recette=recette)

@app.route('/submit', methods=["POST"])
def valider():
    recette = request.form.get("recette")
    total_coef = 0

    for cat, coef in coefficients.items():
        count = int(request.form.get(cat, 0))
        total_coef += count * coef

    # Calculer les quantités
    ingrs = ingredients.get(recette, {})
    donnees = {"Ingrédient": [], "Quantité totale": []}

    for ingr, qte_unitaire in ingrs.items():
        total = round(qte_unitaire * total_coef, 2)
        donnees["Ingrédient"].append(ingr)
        donnees["Quantité totale"].append(total)

    # Générer un fichier Excel en mémoire
    df = pd.DataFrame(donnees)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Ingrédients")
    output.seek(0)

    # Trouver le path du PDF
    safe_name = "_".join(recette.lower().split())
    pdf_path = os.path.join("recettes", f"{safe_name}.pdf")

    if not os.path.exists(pdf_path):
        return f"Erreur : le fichier {pdf_path} est introuvable.", 404

    # Créer un fichier ZIP contenant les deux
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        zipf.writestr(f"ingredients_{recette.lower().replace(' ', '_')}.xlsx", output.getvalue())
        zipf.write(pdf_path, arcname=f"{recette.lower().replace(' ', '_')}.pdf")
    zip_buffer.seek(0)

    # Envoyer le zip
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{recette.lower().replace(' ', '_')}_recette.zip"
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Render provides PORT dynamically
    app.run(host="0.0.0.0", port=port, debug=False)


