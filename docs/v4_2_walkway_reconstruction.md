# v4.2 walkway reconstruction specification

Candidate initial contacts are rising edges of the released left/right contact fields. Step and stride intervals use consecutive contralateral and ipsilateral initial contacts. Spatial metrics require a calibrated rear-foot coordinate in metric units and project displacement onto direction of progression. Cadence is 60 times valid steps divided by the frozen ambulation interval. CV uses sample standard deviation.

The released CSV contains pressure-grid strings in `Walkway_X` and `Walkway_Y`, but the release does not provide a documented grid-to-metric calibration or an explicit rear-foot coordinate. Therefore these strings are not silently treated as metric geometry. Without calibration, step length, stride length, and the eight-input score are not estimable.
