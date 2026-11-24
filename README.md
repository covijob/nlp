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

`fragmentai.jsonl` ir `vektoriai.npy` sugeneruojami iš PDF paleidus kodą arba juos duos Mangirdas, kai bus paruošti.

## Aplankai

```
data/      # duomenys (nėra gite)
models/    # modeliai (nėra gite)
src/       # kodas
web/       # Django svetainė
eval/      # testinės frazės ir teisingi atsakymai
```
