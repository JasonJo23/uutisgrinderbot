# Uutisgrinderbot

Suomenkielinen aamukooste Telegramiin joka päivä noin klo 9 Suomen aikaa.
Kooste käsittelee koko edellisen kalenteripäivän. Pääpaino taloudessa,
suurissa politiikan uutisissa ja muissa merkittävissä tapahtumissa.

## Tila

Koodi ja paikalliset testit on valmisteltu. Pilvipalvelua ei ole vielä otettu
käyttöön, eikä oikeaa API-hakua tai Telegram-lähetystä ole testattu.
Niihin tarvitaan käyttäjän avaimet ja vastaanottajan paritus.

## Käyttöönotto

1. Luo GitHubiin yksityinen `uutisgrinderbot`-repository ja lisää nämä tiedostot
   sen juureen. `render.yaml` ja `bot.py` ovat samalla tasolla.
2. Luo OpenAI API -avain osoitteessa https://platform.openai.com/api-keys ja
   varmista, että API-projektilla on käytettävissä laskutus/rahoitus sekä
   pääsy asetuksessa valittuun malliin. Avainta ei laiteta GitHubiin tai chattiin.
3. Parita Telegram alla olevalla ohjeella. Tarvitset kolme asetusta:
   `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN` ja `TELEGRAM_CHAT_ID`.
4. Valitse Renderissä **New → Blueprint**, yhdistä repository ja anna pyydetyt
   kolme asetusta. Tarkista hinta ennen palvelun luomista. Blueprint luo yhden
   maksullisen cron-palvelun Frankfurtin alueelle; tietokantaa ei tarvita.
5. Tarkista, että build-testit onnistuvat. Tee alla olevat yhteys- ja koekäyttötestit
   ennen kuin luotat päivittäiseen toimitukseen.

## Telegramin paritus

Macissa, Terminalissa, siirry tähän kansioon ja suorita:

```sh
python3 bot.py pair
```

Ohjelma pyytää BotFatherin tokenin piilotettuna. Se ei tallenna tokenia.
Lähetä ohjelman näyttämä kertakäyttöinen `/start ...` -viesti botille
**@Uutisgrinderbot**. Paina sitten Terminalissa Enter.
Ohjelma näyttää `TELEGRAM_CHAT_ID`-arvon, jonka lisäät Renderiin.
Tunnistus estää vieraan käyttäjän `/start`-viestin valitsemisen vastaanottajaksi.
Paritus edellyttää, ettei tällä botilla ole toista getUpdates-lukijaa tai webhookia.
Jos viestiä ei löydy, älä arvaa tunnistetta; selvitä botin nykyiset yhteydet.

## Koekäyttö

Ympäristömuuttujien on oltava asetettuina suoritusympäristössä. Älä kirjoita
avaimia komentoriveille, jotka tallentuvat komentohistoriaan.

```sh
# Vain Telegram-yhteystesti; ei OpenAI-kuluja.
python3 bot.py test-telegram

# Hakee oikeat uutiset ja tulostaa koosteen, ei lähetä Telegramiin. API-kuluja syntyy.
python3 bot.py preview

# Hakee ja lähettää edellisen päivän koosteen heti. API-kuluja syntyy.
python3 bot.py send-now

# Normaali ajo, joka toimii vain Suomen klo 09.00–09.29 käynnistysikkunassa.
python3 bot.py scheduled
```

Renderin kertatestissä voit muuttaa palvelun Start Command -arvoksi
`python bot.py test-telegram`, tallentaa ja käynnistää ajon **Trigger Run** -painikkeella.
Palauta heti sen jälkeen Start Command -arvoksi `python bot.py scheduled`.
Älä tee tätä lähellä aamuajoa. Samoin `send-now` mahdollistaa ensimmäisen oikean
koosteen testin. Tarkista onnistuminen sekä Renderin lokista että Telegramista.
Jos Renderin käyttöliittymän kentät eroavat tästä, käytä palvelun ajantasaisia ohjeita.

## Aikavyöhyke ja toimitus

Renderin ajastukset käyttävät UTC-aikaa. Sama palvelu käynnistyy klo 06 ja 07 UTC.
Ohjelma tekee verkkopyynnöt vain siinä ajossa, joka vastaa Suomen klo 9:ää.
Toinen ajo poistuu heti. Pythonin `Europe/Helsinki`-aikavyöhyke käsittelee
kesä- ja talviajan sekä 23/25 tunnin kalenteripäivät.
Uutishaku alkaa noin klo 9; viesti saapuu sen valmistuttua, joten toimitus voi
olla muutamia minuutteja myöhemmin. Yli puoli tuntia viivästynyt käynnistys ohitetaan.

## Luotettavuus ja rajat

- OpenAI Responses API tekee tuoreet verkkohaut. Malli on vaihdettavissa
  `OPENAI_MODEL`-asetuksella; oletus on `gpt-5.5`.
- Jokaiseen uutiseen pyydetään lähdeviite ja viitteiden URL:t lisätään viestiin.
  Lähteettömät, keskeneräiset ja ilman verkkohakua syntyneet vastaukset hylätään.
  Päivärajaus ja uutisten oikeellisuus ovat silti mallin tekemän tutkimuksen varassa:
  ensimmäiset koosteet on tarkistettava lähteistä. Verkkohaku ei takaa täydellistä kattavuutta.
- Yksi OpenAI-pyyntö per ajo, enintään 8 työkalukutsua ja 6000 tulostokenia.
  Nämä eivät ole euromääräinen kulukatto. Tarkista tilin kulut ja laskutusasetukset.
- Pitkä kooste jaetaan Telegramin pituusrajaan sopiviin numeroituihin viesteihin.
- Lokit eivät sisällä avaimia tai Telegramin tokenin sisältävää pyyntöosoitetta.
- Virhe pysäyttää ajon. Automaattista uudelleenlähetystä ei tehdä, koska
  verkkovirheessä viesti saattaa olla jo perillä. Jos vain osa viesteistä saapui,
  tarkista ne ennen manuaalista uutta ajoa.
- Tässä kevyessä versiossa ei ole pysyvää lähetystietokantaa. Manuaalinen
  uudelleenajo voi lähettää saman päivän koosteen uudelleen. Renderin loki on
  ajohistorian lähde. Ota Renderissä käyttöön epäonnistuneiden ajojen ilmoitukset.
- Botti lähettää yksityisviestejä. Se ei vielä vastaa keskusteluun tai komentoihin
  jatkuvasti; `/start`-viestiä käytetään vain paritukseen.

## Testit ja lähteet

```sh
python3 -m unittest discover -s tests -v
```

- https://render.com/docs/cronjobs
- https://render.com/docs/blueprint-spec
- https://developers.openai.com/api/docs/guides/tools-web-search
- https://core.telegram.org/bots/api

Renderin cron-palvelun vähimmäisveloitus on dokumentaation mukaan 1 USD/kk,
jonka päälle voi tulla käytön mukaisia kuluja. OpenAI veloittaa erikseen.
Tarkistettu 29.10.2026; tarkista tilausnäkymän hinta ennen käyttöönottoa.
