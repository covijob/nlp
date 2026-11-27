# Seimo stenogramų paieškos ir analizės sistema

Seimo stenogramos suskaidomos į fragmentus (kalbėtojas, frakcija, data), o paieška atliekama BGE-M3 vektoriais su raktų filtru arba be jo.

## 1. Nusikopijuoti repozitoriją

Repozitorija viešai prieinama, prisijungti prie jos nereikia:

```
git clone https://github.com/covijob/nlp.git
cd nlp
git checkout savo_branchas
```

Darbo su branchais taisyklės parašytos faile `notes/work_ethic.md` (yra `dev` branche).

## 2. Python aplinka

Reikia Python 3.10+ (rekomenduojama virtuali aplinka).

```
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
python -m spacy download lt_core_news_md
```

## 3. BGE-M3 modelis (~2,2 GB)

Modelis į git nededamas, jį reikia atsisiųsti į `models/bge-m3`:

```
hf download BAAI/bge-m3 --local-dir models/bge-m3 --exclude "onnx/*" "imgs/*" "long.jpg"
```

(`hf` įdiegiamas kartu su `huggingface_hub`. Senesnėse versijose komanda vadinasi `huggingface-cli download`.)

## 4. Duomenys

Stenogramos (PDF) ir iš jų sugeneruoti failai (`fragmentai.jsonl`, `vektoriai.npy`) į git nededami.

Stenogramas atsisiųsk rankiniu būdu iš Seimo svetainės: https://www.lrs.lt/sip/portal.show?p_r=40552&p_k=1

Reikalingi tik du leidiniai: **Nr. 7** ir **Nr. 8**. Kitų nenaudojame. Atsisiųstus PDF padėk į `data/` aplanką.

### Sugeneruoti failai (`fragmentai.jsonl`, `vektoriai.npy`)

Jie sugeneruojami iš PDF paleidus kodą, todėl **kiekvienas gali juos pasidaryti pats**. Bet vektorių skaičiavimas užtrunka (ypač be GPU), todėl dalinamės taip:

1. Vieną kartą juos sugeneruoja vienas žmogus (kurio kompiuteryje greičiausia). Kadangi generavimas dar nepradėtas, vektorius galima suskaičiuoti ir debesyje (pvz. Google Colab su nemokamu GPU), o gautus failus parsisiųsti ir išdalinti kitiems.
2. Jis supakuoja `fragmentai.jsonl` ir `vektoriai.npy` į vieną `.zip` ir atsiunčia grupėje (Teams / Messenger).
3. Visi kiti išpakuoja į `data/`.

Svarbu: `vektoriai.npy` eilučių tvarka turi sutapti su `fragmentai.jsonl`. Jei kas nors pakeičia fragmentavimą (`parse.py`), vektorius reikia perskaičiuoti ir pranešti kitiems, kad atsisiųstų naujus.

## 5. Svetainė

```
cd web
python manage.py migrate
python manage.py runserver
```

Atsidaryk http://127.0.0.1:8000. Paieškai `bge` reikia `data/vektoriai_sample.npy` (arba pilnų `fragmentai.jsonl` ir `vektoriai.npy`) ir įdiegtų `torch` bei `FlagEmbedding`. Jei jų nėra, rodomi atsitiktiniai fragmentai.

## Aplankai

```
data/      # duomenys (nėra gite)
models/    # modeliai (nėra gite)
src/       # kodas
web/       # Django svetainė
eval/      # testinės frazės ir teisingi atsakymai
```
