Completed Nov 2023

Left-right outputs the coordinates of the face as seen in the webcam in 2 dimensions. This simpler version is what will be used in the first person dodging game. To smoothen out the jitteriness of the measurements, a dampening is applied so that only movements with a magnitude and speed above a certain threshold will be measured. Otherwise, in the dodging game, the player will see their avatar twitch erratically.

Face-depth uses some vector math to measure the actual coordinates of the face in 3 dimensions. It is only a rough estimate, using the average distance between eyes to calculate the face's depth. This makes it unaccurate, especially when tilting the head side to side, but allows the measurement to be performed with any kind of webcam.

Face speed calculates the speed of the face's movement in 3 dimentions.

From face depth:
<img width="1370" alt="Screenshot 2024-01-27 at 3 21 10 PM" src="https://github.com/ZifanWang2005/Face-tracking/assets/66435143/0c460bed-2cd1-4887-98f8-80ddc630a610">


