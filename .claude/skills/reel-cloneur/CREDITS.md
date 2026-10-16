# Crédits

Reel Cloneur™ fait partie de Monteur IA, par LeMondeDuMarketing.

Il s'appuie sur des outils et des idées open source. Merci à leurs auteurs.

## Outils utilisés (installés à part, non inclus dans Monteur IA)

- **yt-dlp** (The Unlicense) : téléchargement des vidéos publiques. https://github.com/yt-dlp/yt-dlp
- **curl_cffi** (MIT) : permet à yt-dlp de lire Instagram sans connexion. https://github.com/lexiforest/curl_cffi
- **FFmpeg** (LGPL/GPL) : audio, détection des coupes, extraction des images. https://ffmpeg.org
- **whisper.cpp** (MIT) : transcription locale. https://github.com/ggml-org/whisper.cpp

## Projets dont on s'est inspiré (licence MIT)

Aucun code n'en est copié tel quel ; les grilles et méthodes ci-dessous ont été traduites et
adaptées.

- **watchvideo**, © 2026 Charles J Dove : la grille hook parlé / hook visuel / alignement, les
  formats et la structure en beats (`references/grille-analyse.md`),
  la forme du fichier d'analyse.
- **claude-video**, © 2026 Bradley Bonanno : la chaîne lien → images → transcription lue par l'IA.
- **viral-video-decomposer**, © 2026 sharon-laicc : l'idée du plan de tournage à trous et du
  contrat de sortie (champs de mécanique virale, objet « plan »).
- **video-agent-skills**, © 2026 Melvyn Malherbe : les formules d'accroche et la règle des 3
  accroches par script ; pour le style de montage (son skill `steal`), la fiche par dimensions où
  chaque valeur vient d'une observation, la section « laissé de côté », et la règle de ne jamais
  dépasser l'original (zooms, effets, taille du visage).
- **social-skills**, © 2026 Scrollmark, Inc. : l'anatomie du hook et l'autopsie de contenu.
- **open-edits** (github.com/kevinbadi/open-edits) : pour le style de montage, remesurer la vidéo
  montée avec le même outil que la référence, pour retrouver une règle oubliée.
- **ghost-editor** (github.com/kurbaitaev/ghost-editor) : « un style est un système » (des règles,
  pas des moments), et les valeurs relevées séparées des valeurs estimées.
- **marketingskills** (github.com/coreyhaines31/marketingskills, skill `video`) : noter des règles
  plutôt que des instances, et les 3 à 5 gestes signature d'un montage.

Texte de la licence MIT, qui s'applique à ces projets :

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software
> and associated documentation files (the "Software"), to deal in the Software without
> restriction, including without limitation the rights to use, copy, modify, merge, publish,
> distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
> Software is furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or
> substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
> BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
> NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
> DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
