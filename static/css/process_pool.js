var posBtn = document.getElementById("posBtn");
var negBtn = document.getElementById("negBtn");

var pos_box = document.getElementById("positiveTable");
var neg_box = document.getElementById("negativeTable");
var is_positive = true;

posBtn.onclick = function () {
    is_positive = true;
    if (pos_box.style.display == "none") {
        pos_box.style.display = "block";
        neg_box.style.display = "none";        
        posBtn.className += " active";
        negBtn.classList.remove("active");
    }
}

negBtn.onclick = function () {
    is_positive = false;
    if (neg_box.style.display == "none") {        
        console.log("2");
        pos_box.style.display = "none";
        neg_box.style.display = "block";
        negBtn.className += " active";
        posBtn.classList.remove("active");
    }
}
