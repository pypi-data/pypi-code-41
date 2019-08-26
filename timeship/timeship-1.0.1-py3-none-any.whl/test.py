# -*- coding: utf-8 -*-

import time

import timeship


def main():
    # you have different options to set anchors

    # first: with the help of timeships anchor function
    # set anchor Arrr
    timeship.anchor("Arrr")
    # execute code
    time.sleep(0.1)
    # release anchor Arrr
    timeship.anchor("Arrr", release=True)

    # set anchor Orrr
    timeship.anchor("Orrr")
    # execute some code
    time.sleep(0.4)
    # additionally set anchor Errr
    timeship.anchor("Errr")
    # execute some other code
    time.sleep(0.4)
    # release all active anchors by not specifying a name
    timeship.anchor()

    # second: you can use contexts
    with timeship.Anchor("setup"):
        time.sleep(0.1)


    # nested timing context can be specified with slashes:
    timeship.anchor("xdata/load")
    time.sleep(0.1)
    timeship.anchor()
    timeship.anchor("xdata/augment")
    time.sleep(0.1)
    timeship.anchor()

    # or by nesting contexts:
    with timeship.Anchor("ydata"):
        with timeship.Anchor("load"):
            # execute ydata loading code
            time.sleep(0.2)
        with timeship.Anchor("augment"):
            # execute ydata augmentation code
            time.sleep(0.3)

    # or equivalently:
    with timeship.Anchor("zdata/load"):
        # execute zdata loading code
        time.sleep(0.2)
    with timeship.Anchor("zdata/augment"):
        # execute zdata augmentation code
        time.sleep(0.3)

    # some more contexts for testing
    with timeship.Anchor("a"):
        time.sleep(0.2)
        with timeship.Anchor("b"):
            time.sleep(0.2)
            with timeship.Anchor("c"):
                time.sleep(0.2)
                with timeship.Anchor("d"):
                    time.sleep(0.1)
                    with timeship.Anchor("e"):
                        time.sleep(0.4)
            with timeship.Anchor("f"):
                time.sleep(0.3)
        with timeship.Anchor("g"):
            with timeship.Anchor("h"):
                time.sleep(0.1)
            with timeship.Anchor("i"):
                time.sleep(0.5)

    # timeships plotting function creates a directory (specified by
    # the `dir` argument) with an index.html containing a d3 plot
    # with the timing data which can be viewed through a webbrowser
    timeship.plot()


if __name__ == '__main__':
    main()
