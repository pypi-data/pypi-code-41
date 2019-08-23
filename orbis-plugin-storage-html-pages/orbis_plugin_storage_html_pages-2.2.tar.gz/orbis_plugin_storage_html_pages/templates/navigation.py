navigation = """
<div class="row">
    <div class="col-md-4">
        {prev}
    </div>
    <div class="col-md-4">
        <form id="jump_form" name="jump_form" method="post" action="">
            <p>
                <label>Jump to Index
                    <input type="text" name="jump_input" id="jump_input" />
                </label>
                <input id="jump_button" type="submit" name="button" value="Jump" class="btn btn-secondary" href="#" role="button" />
            </p>
        </form>
    </div>
    <div class="col-md-4">
        {next}
    </div>
</div>
"""
