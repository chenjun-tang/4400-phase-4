

var stuBtn = document.getElementById("stuBtn");
var empBtn = document.getElementById("empBtn");

var student_box = document.getElementById("student");
var employee_box = document.getElementById("employee");
var is_student = true;

stuBtn.onclick = function () {
    is_student = true;
    if (student_box.style.display == "none") {
        student_box.style.display = "block";
        employee_box.style.display = "none";        
        stuBtn.className += " active";
        empBtn.classList.remove("active");
    }
}

empBtn.onclick = function () {
    is_student = false;
    if (employee_box.style.display == "none") {        
        console.log("2");
        student_box.style.display = "none";
        employee_box.style.display = "block";
        empBtn.className += " active";
        stuBtn.classList.remove("active");
    }
}


