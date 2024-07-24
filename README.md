# ParKing

ParKing je web aplikacija za pračenje ulaska, izlaska, te okupiranosti parkirnih mjesta na komercijalnim parkirnim parkovima. Omogućava jednostavan i učinkovit unos novih parkirnih mjesta, te upraljanje istim.
Koristeći aplikaciju ParKing, uvijek znamo točno koliko je slobodnih parkirnih mjesta preostalo, te gdje se slboodna mjesta nalaze. Isto tako pratimo i na jednostavan način naplačujemo usluge parkiranja.

![ParKing_use_case](https://github.com/user-attachments/assets/8c731307-f7aa-423e-9f00-19835e18a84f)


# Instalacija

#### Skidanje koda s GitHub-a:
```
cd ~/Downloads
git clone https://github.com/thecodereule/ParKing.git
cd ParKing
```

#### Pokretanje Docker-a:
```
sudo docker build --tag parking:1.1 --load .
docker ps
docker run -p 5000:8080 parking:1.1
```
