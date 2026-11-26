# Seimo stenogramų paieškos ir analizės sistema: projekto planas

## Tema, tikslas ir uždaviniai

**Tema:** Seimo stenogramų paieškos ir analizės sistemos kūrimas: teksto apdorojimo poveikis semantinės paieškos kokybei.

**Tikslas:** sukurti paprastą sistemą, kuri Seimo stenogramas suskaido į fragmentus su raktu (kalbėtojas, frakcija, data), iš vartotojo frazės ištraukia raktą, pagal jį atfiltruoja fragmentus ir tarp jų atlieka BGE-M3 vektorinę paiešką, bei palyginti šią paiešką su vien vektorine BGE-M3 paieška be filtro.

**Uždaviniai:**

1. Suskaidyti stenogramas į fragmentus ir kiekvienam priskirti raktą: kalbėtoją, frakciją, datą.
2. Lematizuoti tekstą ir žodynais pažymėti paminėtus asmenis ir institucijas.
3. Taisyklėmis atskirti procedūrinį tekstą (registracija, padėkos, žodžio suteikimas).
4. Iš vartotojo frazės ištraukti (galbūt nepilną) raktą ir pagal jį atfiltruoti fragmentus.
5. Atlikti BGE-M3 vektorinę paiešką tarp atfiltruotų fragmentų ir tarp visų fragmentų (be filtro).
6. Sukurti Django svetainę: frazės, tyrimo paleidimas (CPU arba GPU), rezultatai.
7. Palyginti abu paieškos būdus su testinėmis frazėmis (Precision@5) ir patikrinti, ką duoda triukšmo filtras.

## Įrankiai ir failai

Viskas daroma su Python vienoje Git repozitorijoje (`https://github.com/covijob/nlp`). Darbo su Git taisyklės: `work_ethic.md`, aplinkos paruošimas: `README.md`. Aplankas `notes/` yra tik `dev` ir asmeniniuose branchuose, į `prod` nepatenka.

| Ką darome | Kuo |
| --- | --- |
| Failų skaitymas, skaidymas | `pdfplumber` (stenogramos yra PDF), `re`, `pandas` |
| Lematizavimas | `spacy` + `lt_core_news_md` |
| Vektoriai ir paieška | `FlagEmbedding` (BGE-M3), `torch`, `numpy` |
| Svetainė | `django` (SQLite), `matplotlib` grafikams |

```
nlp/
  data/          # stenogramos (PDF), fragmentai.jsonl, vektoriai.npy, zodynai/ (NĖRA gite, žr. README.md)
  models/        # bge-m3/ (NĖRA gite, žr. README.md)
  notes/         # vidiniai dokumentai (tik dev, ne prod)
  src/           # parse.py, enrich.py, noise.py, search.py, evaluate.py
  web/           # Django projektas
  eval/          # frazes.jsonl, teisingi.jsonl
  README.md
  requirements.txt
```

**Duomenų formatas:** vienas fragmentas = viena eilutė `fragmentai.jsonl`:

```json
{"id": 42, "data": "2024-05-07", "posedis": "rytinis Nr. 370", "kalbetojas": "L. Jonauskas", "frakcija": "LSDPF", "tekstas": "...", "tekstas_lema": "...", "esybes": ["Seimas"], "triuksmas": false}
```

`vektoriai.npy` eilučių tvarka sutampa su `fragmentai.jsonl`.

`data/` ir `models/` į git nededami (jie yra `.gitignore`), todėl didelius failus kiekvienas pasiima atskirai pagal `README.md`. Mažas `eval/` aplankas ir `fragmentai_sample.jsonl` (jei lieka mažas) gali būti gite.

## Etapai

### 1. Skaidymas į fragmentus (`parse.py`)

- Stenogramos yra PDF (`data/*.pdf`). Tekstas iš PDF ištraukiamas su `pdfplumber`, tada skaitomas eilutė po eilutės, `re` ieško datos („2024 m. gegužės 7 d.“), posėdžio („Rytinis posėdis Nr. 370“) ir kalbėtojo eilutės („L. JONAUSKAS (LSDPF).“).
- Viskas nuo vieno kalbėtojo iki kito yra vienas fragmentas. Ilgesni nei 300 žodžių pasisakymai paprastai perkerpami į dalis po ~300 žodžių.
- Išmetamos šiukšlės: „(Gongas)“, išnašų žymos, tuščios eilutės, PDF puslapių antraštės ir numeriai.
- Jei frakcija nenurodyta, ji paimama iš kito to paties žmogaus pasisakymo.
- Patikra: peržiūrėti 20 atsitiktinių fragmentų.

### 2. Lematizavimas ir esybės (`enrich.py`)

- spaCy `lt_core_news_md` paverčia tekstą lemomis, išmetami stop-žodžiai → `tekstas_lema`.
- Esybės randamos paprastais žodynais: Seimo narių pavardės (iš kalbėtojų sąrašo) ir ~30 institucijų (Vyriausybė, NATO, ES…), ieškoma lematizuotame tekste.
- Patikra: 20 fragmentų rankiniu būdu.

### 3. Triukšmo filtras (`noise.py`)

- Fragmentas yra triukšmas, jei jis trumpesnis nei 15 žodžių arba turi procedūrinę frazę („užsiregistravo“, „dėkoju, posėdžio pirmininke“, „balsuojame“…).
- Patikra: rankiniu būdu pažymėti 100 fragmentų ir pažiūrėti, kiek taisyklė atspėja.

### 4. Vektoriai (`search.py`)

```python
from FlagEmbedding import BGEM3FlagModel
modelis = BGEM3FlagModel("models/bge-m3", use_fp16=True)  # vietinis modelis, žr. README.md
v = modelis.encode(tekstai, batch_size=32, max_length=512)["dense_vecs"]
np.save("data/vektoriai.npy", v)
```

Visų fragmentų vektoriai suskaičiuojami vieną kartą (geriausia Google Colab su GPU) ir išsaugomi.

### 5. Paieška: raktas + BGE-M3 (`search.py`)

Kiekvienas fragmentas jau turi raktą iš 1 etapo: **KALBĖTOJAS, FRAKCIJA, DATA**.

1. **Rakto ištraukimas iš frazės** (`istraukti_rakta(fraze)`): tais pačiais žodynais kaip 2 etape randama pavardė, frakcija, o `re` randa metus ar mėnesį. Pvz., „Ką Skvernelis kalbėjo apie energetiką 2022 m.“ → `{kalbetojas: "S. Skvernelis", metai: 2022}`. Raktas gali būti nepilnas: naudojami tik rasti laukai.
2. **Filtravimas:** `pandas` paliekami tik fragmentai, atitinkantys raktą, ir `triuksmas == False`.
3. **Vektorinė paieška:** frazės BGE-M3 vektorius × likusių fragmentų vektoriai, imami 5–10 su didžiausiu balu.
4. Jei po filtro nelieka nė vieno fragmento, ieškoma be filtro.

Lyginami du būdai, abu per tą pačią funkciją `ieskoti(fraze, metodas, k)`:

| Metodas | Kaip veikia |
| --- | --- |
| `bge` | tik BGE-M3 vektorinė paieška tarp visų fragmentų |
| `raktas_bge` | raktas → filtras → BGE-M3 vektorinė paieška |

### 6. Vertinimas (`evaluate.py`)

- 20–30 testinių frazių (`eval/frazes.jsonl`). Kiekvienai surašoma, kurie fragmentai yra teisingi (`eval/teisingi.jsonl`): žmogus peržiūri abiejų metodų top-10 ir pažymi tinkamus.
- Metrika: Precision@5 = kiek iš pirmų 5 rezultatų yra tinkami, padalinta iš 5.
- Frazės būna dviejų rūšių: su raktu (paminėtas kalbėtojas ar metai) ir be jo. Lentelė: `bge` ir `raktas_bge` atskirai abiem rūšims, su triukšmo filtru ir be jo, plius kiek raktų ištraukta teisingai.

## Django svetainė

Svetainė turi tris puslapius, viskas su paprastais Django šablonais ir SQLite.

| Puslapis | Kas jame yra |
| --- | --- |
| Frazės | iš anksto įrašytų frazių sąrašas (iš `eval/frazes.jsonl`), laukelis savo frazei pridėti |
| Tyrimas | pažymimos frazės, pasirenkamas metodas (tik BGE / raktas + BGE), CPU arba GPU, mygtukas **Paleisti** |
| Rezultatai | kiekvienai frazei top-5 fragmentai (kalbėtojas, data, ištrauka), trukmė, Precision@5, jei frazė turi teisingus atsakymus; du grafikai: paminėjimai per mėnesius ir pagal frakcijas |

- Modeliai: `Fraze(tekstas)` ir `Tyrimas(frazes, metodas, irenginys, rezultatai JSON, trukme)`.
- Tyrimas vykdomas tiesiog paspaudus mygtuką: puslapis palaukia, kol baigsis, ir parodo rezultatus. Jokio fono darbo.
- CPU / GPU: `BGEM3FlagModel("models/bge-m3", devices=irenginys)`, kur `irenginys` yra `"cpu"` arba `"cuda"`. Jei `torch.cuda.is_available()` grąžina False, GPU pasirinkimas nerodomas. (Senesnėse FlagEmbedding versijose argumentas vadinasi `device`.)
- Grafikai piešiami su `matplotlib` ir rodomi kaip paveikslėlis.

## Darbų pasiskirstymas

Kiekvienas dirba savo failuose. Pirmiausia Mangirdas paruošia repozitoriją ir pavyzdinį failą `fragmentai_sample.jsonl` (~500 fragmentų iš 2–3 stenogramų), o tada visi dirba lygiagrečiai su tuo pavyzdžiu. Kiekvienas dirba savo asmeniniame branche ir merginą tik į `dev` (žr. `work_ethic.md`).

**Mangirdas: pagrindas, 1 etapas, svetainė**

- [x] Repozitorija, `requirements.txt`, duomenų formatas, tuščios funkcijos visiems failams
- [x] `fragmentai_sample.jsonl`
- [ ] Visas 1 etapas: `parse.py` ir pilnas `fragmentai.jsonl`
- [ ] Django svetainė (3 puslapiai) ir visų modulių prijungimas prie jos

**Narys 2: teksto apdorojimas ir raktas**

- [ ] 2 etapas: lematizavimas, pavardžių, frakcijų ir institucijų žodynai (`enrich.py`)
- [ ] Rakto ištraukimas iš frazės: `istraukti_rakta(fraze)`
- [ ] 3 etapas: triukšmo taisyklės (`noise.py`)

**Narys 3: vektoriai ir paieška**

- [ ] 4 etapas: BGE-M3 vektoriai, `vektoriai.npy`
- [ ] 5 etapas: `ieskoti()` su `bge` ir `raktas_bge` (filtras pagal raktą + vektorinė paieška)
- [ ] CPU ir GPU palaikymas modelio įkėlimui

**Narys 4: užklausos ir vertinimas**

- [ ] 20–30 testinių frazių formulavimas (`eval/frazes.jsonl`), su raktu ir be jo: jos bus numatytosios frazės svetainėje
- [ ] Teisingų atsakymų žymėjimas (`eval/teisingi.jsonl`)
- [ ] `evaluate.py`: Precision@5 abiem metodams ir rakto ištraukimo tikslumas

**Kol kito nario dalis nepadaryta**, naudojamas paprastas pakaitalas: `tekstas_lema = tekstas.lower()`, `triuksmas = False`, `istraukti_rakta()` grąžina tuščią raktą, `ieskoti()` grąžina atsitiktinius fragmentus.