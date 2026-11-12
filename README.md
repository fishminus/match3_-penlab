# match3_-penlab
Dette er et match 3 spill for INF100 UiB

## Installering
For å spille dette på egen maskin trenger man disse eksterne modulene:
1. uib-inf100-graphics
`python -m pip install uib-inf100-graphics`
2. pygame (for lyder)
`python -m pip install pygame`

og python (åpenbart)

## Bruk
Når spillet er installert, så åpner man `"MATCH_3.py"`, man kan også redigere `assets/json.levels` for å endre banene sine dimensjoner og vanskelighets grad. Man kan også endre bildene under `assets/`, men sørg for å beholde bildenavnene, eller endre bildelenkene under `MATCH_3.py`

## Demo
`https://www.youtube.com/watch?v=D_BjfVM3yY4`

## Bruk av AI
match3_logic.py er laget av meg, også har jeg integrert komponenter fra Claude AI for UX, men all kode er kvalitetssikret.
