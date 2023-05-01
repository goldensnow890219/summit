class AsyncFrom {
    constructor(form) {
        this.form = form;
        this.form.addEventListener( "submit", ( event ) => {
            event.preventDefault();
            this.sendData();
        });
    }

    sendData(event) {
        const request = new XMLHttpRequest();
        const formData = new FormData( this.form );

        request.addEventListener( "load", (event) => {
          this.form.innerHTML = event.target.responseText;
        });

        request.addEventListener( "error", ( event ) => {
          this.form.innerHTML = 'Oops! Something went wrong.';
        });

        // Set up our request
        request.open( "POST",  `${this.form.action}?embeded=true`);

        // The data sent is what the user provided in the form
        request.send( formData );
  }
}

(function() {
    [...document.getElementsByClassName('contact-form')].forEach(
        (form) => new AsyncFrom(form)
    );
})();