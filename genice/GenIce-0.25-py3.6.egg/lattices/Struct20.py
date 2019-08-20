# coding: utf-8
"""
Data source: Dutour Sikirić, Mathieu, Olaf Delgado-Friedrichs, and Michel Deza. “Space Fullerenes: a Computer Search for New Frank-Kasper Structures” Acta Crystallographica Section A Foundations of Crystallography 66.Pt 5 (2010): 602–615.

Cage composition:
 (12,14,15,16) = (10,4,4,2,)
"""

pairs="""
89 93
54 68
17 108
11 58
54 64
28 42
26 42
22 71
109 85
66 37
89 60
1 96
16 25
54 102
46 6
0 89
13 47
98 62
89 73
5 65
12 55
80 79
69 60
39 47
32 53
33 56
70 67
40 103
104 63
10 20
2 77
65 6
76 60
86 70
5 17
29 24
17 73
46 0
21 19
53 41
47 68
38 87
67 90
26 19
80 72
46 85
15 110
43 93
29 107
58 9
2 58
75 102
109 59
53 74
56 76
65 91
1 48
57 74
26 59
90 68
84 6
3 104
3 106
44 31
74 97
76 98
15 92
43 100
23 40
8 52
84 98
38 37
97 95
27 103
61 88
12 22
14 21
82 107
103 110
30 20
14 101
30 63
46 79
112 100
15 43
12 104
33 90
47 18
86 95
82 113
8 74
1 94
105 107
48 49
82 63
56 100
34 66
22 44
96 78
4 55
39 25
44 27
66 86
101 83
10 57
105 106
3 29
30 7
26 110
51 78
62 72
34 52
35 57
34 75
92 79
18 64
0 59
106 19
80 99
111 9
85 99
21 69
81 103
23 71
53 20
22 42
2 97
13 84
92 62
112 108
105 36
71 110
10 48
31 21
38 45
87 75
62 71
80 93
45 102
33 13
15 0
12 32
61 75
1 36
5 16
5 37
30 106
13 91
67 25
39 86
39 88
66 91
81 72
27 19
111 49
54 108
43 81
14 113
87 49
10 77
82 55
35 49
40 113
112 90
28 4
27 7
60 99
52 95
111 37
51 95
51 94
44 72
93 108
45 33
48 58
77 63
94 107
64 79
73 6
50 100
85 98
91 102
28 109
56 73
35 61
23 109
2 41
11 94
34 9
3 42
8 96
88 9
45 17
14 105
81 76
83 24
7 113
83 36
92 50
20 36
24 41
8 83
4 101
16 112
96 87
35 67
88 97
11 52
69 59
61 68
18 50
23 55
16 18
31 99
11 24
70 78
65 64
4 29
32 7
51 77
111 25
57 78
84 50
38 70
40 69
28 31
104 41
32 101
"""

waters="""
0.625 0.5 0.88464
0.69217 0.30239 0.42828
0.30783 0.69761 0.42828
0.5 0.625 0.61536
0.81717 0.82261 0.63422
0.625 0.5 0.11536
0.82261 0.625 0.0
0.18283 0.17739 0.63422
0.875 0.0 0.40942
0.5 0.69217 0.30328
0.30783 0.30239 0.42828
0.69217 0.69761 0.42828
0.18283 0.82261 0.63422
0.0 0.875 0.09058
0.81717 0.17739 0.63422
0.375 0.5 0.88464
0.375 0.5 0.11536
0.69761 0.30783 0.07172
0.30239 0.69217 0.07172
0.5 0.30783 0.69672
0.375 0.17739 0.5
0.69217 0.18283 0.71558
0.30783 0.81717 0.71558
0.0 0.625 0.7467
0.625 0.82261 0.5
0.30783 0.5 0.19672
0.5 0.5 0.75
0.30783 0.18283 0.71558
0.69217 0.81717 0.71558
0.69217 0.69761 0.57172
0.30783 0.30239 0.57172
0.625 0.0 0.7533
0.125 0.0 0.59058
0.0 0.125 0.09058
0.69217 0.81717 0.28442
0.30783 0.18283 0.28442
0.625 0.17739 0.5
0.69217 0.5 0.19672
0.81717 0.30783 0.21558
0.18283 0.69217 0.21558
0.0 0.375 0.7467
0.375 0.82261 0.5
0.5 0.69217 0.69672
0.30239 0.30783 0.92828
0.375 0.0 0.7533
0.82261 0.18283 0.13422
0.69761 0.69217 0.92828
0.17739 0.81717 0.13422
0.5 0.375 0.38464
0.5 0.30783 0.30328
0.17739 0.625 0.0
0.0 0.5 0.41272
0.81717 0.82261 0.36578
0.25 0.0 0.5
0.5 0.0 0.08728
0.0 0.69761 0.64978
0.0 0.25 0.0
0.18283 0.17739 0.36578
0.5 0.625 0.38464
0.69217 0.5 0.80328
0.82261 0.18283 0.86578
0.375 0.0 0.2467
0.17739 0.81717 0.86578
0.18283 0.5 0.54364
0.5 0.81717 0.04364
0.69761 0.69217 0.07172
0.81717 0.69217 0.21558
0.18283 0.30783 0.21558
0.30239 0.0 0.14978
0.81717 0.30783 0.78442
0.0 0.375 0.2533
0.18283 0.69217 0.78442
0.30239 0.0 0.85022
0.82261 0.375 0.0
0.125 0.0 0.40942
0.625 0.0 0.2467
0.0 0.125 0.90942
0.18283 0.5 0.45636
0.0 0.30239 0.35022
0.5 0.81717 0.95636
0.5 0.0 0.91272
0.17739 0.18283 0.86578
0.0 0.5 0.58728
0.75 0.0 0.5
0.0 0.75 0.0
0.82261 0.81717 0.86578
0.0 0.625 0.2533
0.69217 0.18283 0.28442
0.30783 0.81717 0.28442
0.69761 0.30783 0.92828
0.17739 0.18283 0.13422
0.82261 0.81717 0.13422
0.30239 0.69217 0.92828
0.5 0.18283 0.95636
0.81717 0.5 0.45636
0.0 0.69761 0.35022
0.81717 0.17739 0.36578
0.18283 0.82261 0.36578
0.0 0.875 0.90942
0.69761 0.0 0.85022
0.17739 0.375 0.0
0.875 0.0 0.59058
0.69761 0.0 0.14978
0.18283 0.30783 0.78442
0.30783 0.69761 0.57172
0.69217 0.30239 0.57172
0.5 0.375 0.61536
0.81717 0.5 0.54364
0.5 0.18283 0.04364
0.81717 0.69217 0.78442
0.30783 0.5 0.80328
0.5 0.5 0.25
0.30239 0.30783 0.07172
0.0 0.30239 0.64978
"""

coord= "relative"

cages="""
12 -0.5 0.23132 -0.17456
12 -0.5 0.5 0.5
12 -0.23132 -0.5 0.32544
14 0.0 -0.20955 0.5
12 0.5 0.23132 0.17456
14 -0.20955 0.0 0.0
15 0.5 0.0 -0.61233
16 0.0 0.0 0.25
15 -0.5 0.0 0.61233
12 -0.5 -0.23132 -0.17456
12 -0.5 -0.23132 0.17456
14 0.0 0.20955 0.5
12 0.5 0.5 0.0
12 -0.23132 0.5 0.67456
12 0.23132 0.5 -0.67456
14 0.20955 0.0 0.0
16 0.0 0.0 0.75
15 0.0 0.5 0.11233
15 0.0 0.5 -0.11233
12 0.23132 -0.5 0.67456
"""

bondlen = 3


cell = """
13.378504487123072 13.378504487123072 32.0748344185102
"""

density = 0.5935496386238698



from genice.cell import cellvectors
cell = cellvectors(a=13.378504487123072,
                   b=13.378504487123072,
                   c=32.0748344185102)
