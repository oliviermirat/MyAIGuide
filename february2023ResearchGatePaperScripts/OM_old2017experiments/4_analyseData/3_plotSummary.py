import pickle

import matplotlib.pyplot as plt

input = open("localData.txt", "rb")
localData = pickle.load(input)
input.close()

symptoms = localData[0]
environment = localData[1]
environment[:, 0] = environment[:, 0] / 3600
environment[:, 34] = environment[:, 34] / 60  # Ubuntu Time to minutes #
cond = environment[:, 34] < 0
environment[cond, 34] = 0  # Removes zeros from list #
environment[:, 35] = (
    environment[:, 35] + 0.75 * environment[:, 38]
)  # Add riding car to driving time #
environment[:, 35] = environment[:, 35] / 60  # Car Time to minutes #

xaxis = localData[2]

# Plot Data


def plotSymp(sub=0):
    if sub:
        plt.subplot(sub)
    else:
        plt.figure()
    labels = ["Knees", "Head", "Hands"]
    for idx, lab in enumerate(labels):
        plt.plot(xaxis, symptoms[:, idx], label=lab)
    leg = plt.legend(loc="upper center", shadow=True)
    if leg:
        leg.draggable()
    plt.draw()


def plotEnv(labels, sub=0):
    if sub:
        plt.subplot(sub)
    else:
        plt.figure()
    for lab in labels:
        plt.plot(xaxis, environment[:, lab[0]], label=lab[1])
    leg = plt.legend(loc="upper center", shadow=True)
    if leg:
        leg.draggable()
    plt.draw()


if 0:

    plotSymp()

    plotEnv([[9, "Keys"], [10, "Clicks"]])

    plotEnv([[0, "Windows Time"], [34, "Ubuntu Time"], [35, "Car Time"]])

    plotEnv([[11, "Calories"], [12, "Steps"]])

    plotEnv(
        [
            [21, "Road Bike Cal"],
            [13, "Alpi Ski Cal"],
            [15, "Climbing Cal"],
            [17, "Down Ski Cal"],
            [23, "Swimming Cal"],
            [25, "Via Ferrata Cal"],
            [27, "Walk Cal"],
            [19, "Mt Bike Cal"],
        ]
    )

    plotEnv(
        [
            [21 + 1, "Road Bike Step"],
            [13 + 1, "Alpi Ski Step"],
            [15 + 1, "Climbing Step"],
            [17 + 1, "Down Ski Step"],
            [23 + 1, "Swimming Step"],
            [25 + 1, "Via Ferrata Step"],
            [27 + 1, "Walk Step"],
            [19 + 1, "Mt Bike Step"],
        ]
    )

    plotEnv(
        [
            [5, "Road Bike Dur"],
            [1, "Alpi Ski Dur"],
            [2, "Climbing Dur"],
            [3, "Down Ski Dur"],
            [6, "Swimming Dur"],
            [7, "Via Ferrata Dur"],
            [8, "Walk Dur"],
            [4, "Mt Bike Dur"],
        ]
    )


# Plot Data All Together

if 1:
    plt.figure()

    plotSymp(321)
    plotEnv([[9, "Keys"], [10, "Clicks"]], 323)
    plotEnv([[0, "Windows Time"], [34, "Ubuntu Time"], [35, "Car Time"]], 325)
    plotSymp(322)
    plotEnv([[11, "Calories"], [12, "Steps"]], 324)
    plotEnv(
        [
            [21, "Road Bike Cal"],
            [13, "Alpi Ski Cal"],
            [15, "Climbing Cal"],
            [17, "Down Ski Cal"],
            [23, "Swimming Cal"],
            [25, "Via Ferrata Cal"],
            [27, "Walk Cal"],
            [19, "Mt Bike Cal"],
        ],
        326,
    )

if 1:
    plt.show()


# Printing Data


def printData(xaxis, data, col, deb, end):
    for i in range(deb, end):
        print(xaxis[i], data[i, col])


printData(xaxis, environment, 12, 1, 10)
