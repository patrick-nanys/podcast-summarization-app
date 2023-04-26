function validateForm() {
    let email = document.forms["myform"]["email"].value;
    let pwd = document.forms["myform"]["pwd"].value;
    if (email == "" || pwd == "") {
      alert("Name and password must be filled out");
      return false;
    }
  }