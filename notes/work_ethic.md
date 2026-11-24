# Kaip dirbame su Git

Šis dokumentas skirtas visiems projekto dalyviams

## Branchai

| Branchas | Paskirtis |
|---|---|
| `prod` | Produkcinis kodas. **Čia niekas nieko nemergina ir nepushina.** |
| `dev` | Bendras darbo branchas. Čia visi sumergina savo darbą. |
| `mangirdas`, `arnas`, `andrius`, `mykolas` | Asmeniniai branchai. Kiekvienas dirba tik savo. |

## Pagrindinės taisyklės

1. **Dirbk tik savo branche.** Niekada nekeisk kodo tiesiogiai `dev` ar `prod` branche.
2. **Savo darbą sumergink į `dev`**, kai jis veikia ir yra pakankamai baigtas.
3. **Nemerginkite į `prod`.** Tai atliks Mangirdas, kai bus reikalinga.
4. **Aplankas `notes/` į `prod` nepatenka.** Jis skirtas tik vidiniam darbui, todėl jį palikite tik `dev` ir asmeniniuose branchuose.
5. Prieš pradėdamas dirbti, pasiimk naujausią `dev` (žr. žemiau), kad išvengtum konfliktų.
6. Commit žinutes rašyk trumpai ir aiškiai, pvz. `Add text cleaning function`.
7. Jei kyla konfliktų ar nesi tikras, ką daryti, geriau paklausk, nei spėliok.

## Komandos

### Pirmas kartas: nusikopijuoti projektą
```
git clone https://github.com/covijob/nlp.git
cd nlp
git checkout savo_vardas
```
(vietoj `savo_vardas` rašyk `arnas`, `andrius`, `mykolas` ir pan.)

### Kasdienis darbas savo branche
```
git checkout savo_vardas      # pereiti į savo branchą
git status                    # pažiūrėti, kas pakeista
git add .                     # paruošti visus pakeitimus
git commit -m "Aprašymas"     # išsaugoti pakeitimus
git push                      # nusiųsti į GitHub
```

### Pasiimti naujausią `dev` į savo branchą
Daryk tai prieš pradėdamas dirbti ir prieš merginant į `dev`.
```
git checkout dev
git pull
git checkout savo_vardas
git merge dev
```

### Sumerginti savo darbą į `dev`
```
git checkout dev
git pull
git merge savo_vardas
git push
git checkout savo_vardas      # grįžti dirbti į savo branchą
```

## Ko NEDARYTI

- Nedaryk `git push` ar `git merge` į `prod`.
- Nenaudok `git push --force`.
- Nedirbk tiesiogiai `dev` branche.
- Nedaryk commit su dideliais duomenų failais ar slaptažodžiais.

