# How we rebuilt Glakavank in 3D

theme: tech

place: glakavank

Glakavank, the monastery of Karapet above the plain of Mush, stood for fifteen centuries. After 1915 it was destroyed, and almost nothing of it is left. Its first abbot, Zenob Glak, wrote the History of Taron, which you can read in our Library. We wanted to see the monastery again as it stood, so we rebuilt it in 3D. This short video shows how.

![Glakavank: how the 3D model was made](youtube:03_P9EoYrjE glakavank-video.jpg)

## What we had

Only old pictures. The English traveller H. F. B. Lynch photographed the monastery in 1893 and published the photographs in his book Armenia: Travels and Studies (1901): the walls from the south, the church with its belfry, the two chapels with their drums. Other photographs were taken before 1915. And there is a plan of the church, drawn after R. Hewsen's historical atlas of Armenia. We keep copies of all of them with the model.

## Built in code

The model is made in Blender, but not by hand: a Python script builds every part of it, wall by wall. Openings are cut into solid walls, arches get their mouldings, the drums are laid stone by stone in light and dark, and the stone itself comes from photographs of real stone (Poly Haven). The sizes come from the plan; the heights and the shapes come from the photographs. The same script makes the model that you can turn in your browser on the 3D map page of nxGir.

## Part by part

The first version looked right from afar but missed much. So we went through it part by part, each time putting the photograph next to the model, and fixed what was different.

![The belfry: a photograph of 1893 and the model](glakavank-belfry.jpg)

> The belfry: Lynch's photograph and the model

The belfry was the hardest. Its lower stage turned out to be an octagon, four wide faces with pointed arches and four narrow corners, each with a tall niche carved into it and a small shrine at its foot. The arches of the upper stage are cut into five lobes. We measured its proportions again from the photographs: the gables are low, and their tops meet the foot of the upper stage.

![The two drums: a photograph of 1893 and the model](glakavank-drums.jpg)

> The drums of the two chapels, Lynch's photograph and the model

The two drums looked alike in the first model, but they are not: one is a patchwork of light and dark stone with a straight cone, the other has a ring of tall blind arches and a cone curved like a bell. Then came the hall, with its few windows, thin dark courses and the clay jars lying along its wall; the roofs round the drums; the front of the porch with its tall portal; and the outer walls, stepping down the slope as Lynch saw them from the south.

## What is guessed

This is a reconstruction. The sizes are estimates, the inside of the church is not built, and where no photograph shows a part (the north corners of the walls, for one), we had to guess. If you know of other photographs or drawings of Glakavank, write to us: every new picture makes the model truer.
