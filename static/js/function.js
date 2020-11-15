function validate(){
    var pwd1 = document.getElementById("password").value;
    var pwd2 = document.getElementById("conf_pwd").value;
    <!-- compare two passwds -->
    if(pwd1 == pwd2) {
        if(pwd1.length < 8){
            document.getElementById("tips").innerHTML="<font color='red'>Password must be at least 8 characters in size.</font>";
            document.getElementById("mySubmit").disabled = true;
        }else{
            document.getElementById("tips").innerHTML="<font color='green'>Passwords are consistent.</font>";
            document.getElementById("mySubmit").disabled = false;
        } 
    }
    else {
        document.getElementById("tips").innerHTML="<font color='red'>Passwords are not consistent.</font>";
        document.getElementById("mySubmit").disabled = true;
    }
}
