# 2026_SIM_Project

### Utilisation

`python3 main.py [scene_file]`

### Fichier scène

Le fichier scène est un ficher json.

Le json possède un élément racine nommé `élément`.

L'entrée `elements` de type liste d'objet chacun des entrées de la liste correspond a un élément de la scène.

Un élément de la scène a pour entrée
- `object` avec le chemin vers le fichier ply de l'objet (requis)
- `texture` avec le chemin vers le fichier png de l'objet (optionel: si omit une texture blanche uniforme est appliqué)
- `offset` le decalage de l'objet dans la scène (optionel)


#### Description

```json
{
    "elements": [
        {
            "object": "<path to ply file>",
            "texture": "<path to png file>",
            "offset": [offset_x, offset_y, offset_z]
        }
    ]
}
```