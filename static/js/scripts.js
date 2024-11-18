function showUpdateSuccess() {
    if (document.querySelector('.errorlist')) {
        alert("Profile update failed. Please check the form for errors.");
    } else {
        alert("Profile updated successfully!");
    }
}