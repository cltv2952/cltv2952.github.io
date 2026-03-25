function toggle_collapse(comment_div) {
    var button = comment_div.getElementsByClassName("toggle_hide_button")[0];
    var collapsible = comment_div.getElementsByClassName("collapsible")[0];
    if (collapsible.classList.contains("hidden")) {
        collapsible.classList.remove("hidden");
        button.innerText = "[-]";
    } else {
        collapsible.classList.add("hidden");
        button.innerText = "[+]";
    }
}