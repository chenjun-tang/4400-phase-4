var stuBtn = document.getElementById("stuBtn");
var empBtn = document.getElementById("empBtn");

var student_box = document.getElementById("student");
var employee_box = document.getElementById("employee");

stuBtn.onclick = function () {
    if (student_box.style.display == "none") {
        student_box.style.display = "block";
        employee_box.style.display = "none";
    }
}

empBtn.onclick = function () {
    console.log("1");
    if (employee_box.style.display == "none") {        
        console.log("2");
        student_box.style.display = "none";
        employee_box.style.display = "block";
    }
}
