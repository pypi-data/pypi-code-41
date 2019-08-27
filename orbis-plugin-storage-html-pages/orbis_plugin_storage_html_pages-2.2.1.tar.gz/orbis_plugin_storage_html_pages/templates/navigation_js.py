navigation_js = """
<script type="text/javascript">
document.getElementById("jump_button").onclick = function() {
    {
        var jump_input_var = document.getElementById('jump_input').value;
        window.location.href = jump_input_var + ".html";
        return false;
    }
};
</script>
"""
