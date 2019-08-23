# -*- coding: utf-8 -*-
html_body = """
<!doctype html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Orbis-Eval</title>
    {arrow_key_navigation}
    {bootstrap_core_css}
    {html_css}
</head>

<body>
    <main role="main">
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-12">
                    <h1>Orbis</h1>
                </div>
            </div>
            {orbis_header}
            {item_header}
        </div>

        <div class="container-fluid">
            {navigation}
            <!-- Example row of columns -->

            <div class="row">
                {gold_corpus}
                {predicted_corpus}
            </div>

            <div class="row">
                {gold_entities}
                {predicted_entities}
            </div>

        </div>
    </main>
    {bootstrap_core_js}
</body>
{navigation_js}

</html>
"""
