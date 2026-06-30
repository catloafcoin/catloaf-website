function copyCA() {
    const ca = "GEEQMeTNRYvQKBHZo2jEaHd7j93AZugmSa6UsktJpump";

    navigator.clipboard.writeText(ca).then(() => {
        alert("Contract Address copied!");
    });
}

window.onload = function () {
    console.log("$CLOAF website loaded.");
};
