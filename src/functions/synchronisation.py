from src.classes.transition import Transition


def getEpsilon(automate):
    return next(
        (lettre for lettre in automate.alphabet.lettres if lettre.epsilon), None
    )


def getEtatAsynchrone(etat, epsilon=None, parents=None):
    if parents is None:
        parents = set()
    elif etat in parents:
        return set()

    if epsilon is None:
        epsilon = getEpsilon(etat.automate)
    if epsilon is None:
        return set()

    etatsAsynchrones = set()

    for etatAsynchrone in etat.getNextEtat(epsilon):
        etatsAsynchrones.add(etatAsynchrone)

        if etatAsynchrone not in parents:
            etatsAsynchrones.update(
                getEtatAsynchrone(
                    etatAsynchrone,
                    parents.union(
                        {
                            etat,
                        }
                    ),
                )
            )

    return etatsAsynchrones


def getNextEtatRec(etat, lettre, parents=None):
    if parents is None:
        parents = set()
    elif etat in parents:
        return set()

    etatSuivant = etat.getNextEtat(lettre)

    for etatSuiv in etatSuivant.copy():
        etatSuivant.update(getEtatAsynchrone(etatSuiv))

    for etatAsynchrone in getEtatAsynchrone(etat):
        if etatAsynchrone not in parents:
            etatSuivant.update(
                getNextEtatRec(
                    etatAsynchrone,
                    lettre,
                    parents.union(
                        {
                            etat,
                        }
                    ),
                )
            )

    return etatSuivant


def epsilonInitial(etat, parents=None):
    if etat.initial:
        return True

    if parents is None:
        parents = set()
    elif etat in parents:
        return False

    epsilon = getEpsilon(etat.automate)
    if epsilon is None:
        return etatSuivant

    return any(
        etatAsynchrone not in parents
        and epsilonInitial(
            etatAsynchrone,
            parents.union(
                {
                    etat,
                }
            ),
        )
        for etatAsynchrone in etat.getPreviousEtat(epsilon)
    )


def epsilonTerminal(etat, parents=None):
    if etat.terminal:
        return True

    if parents is None:
        parents = set()
    elif etat in parents:
        return False

    epsilon = getEpsilon(etat.automate)
    if epsilon is None:
        return etatSuivant

    return any(
        etatAsynchrone not in parents
        and epsilonTerminal(
            etatAsynchrone,
            parents.union(
                {
                    etat,
                }
            ),
        )
        for etatAsynchrone in etat.getNextEtat(epsilon)
    )


def synchronize(automate, file=None):
    automateSynchrone = automate.copy()

    if not automate.checkAsynchrone(file=file):
        return automate

    lettres = [
        lettre for lettre in automateSynchrone.alphabet.lettres if not lettre.epsilon
    ]

    for etat in automateSynchrone.etats:
        for lettre in lettres:
            etatSuivant = getNextEtatRec(etat, lettre)
            etatSuivant -= etat.getNextEtat(lettre)

            for etatSuiv in etatSuivant:
                Transition(etat, etatSuiv, lettre)

        if epsilonInitial(etat):
            etat.initial = True
            automateSynchrone.etatsInitiaux.add(etat)

        if epsilonTerminal(etat)(etat):
            etat.terminal = True
            automateSynchrone.etatsTerminaux.add(etat)

    for transition in automateSynchrone.transitions.copy():
        if transition.lettre.epsilon:
            transition.remove()

    return automateSynchrone
