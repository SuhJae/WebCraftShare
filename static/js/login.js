const {createApp, ref} = Vue;

const app = {
    data() {
        return {
            username: '',
            password: '',
            isSubmitting: false,
            usernameValid: null,
            passwordError: false,
            passwordErrorMsg: '',
        };
    },
    computed: {
        isFormInvalid() {
            return this.usernameValid === false || !this.password;
        },
    },
    methods: {
        async checkUsernameValidity() {
            if (!this.username) {
                this.usernameValid = null;
                return;
            }
            try {
                const response = await fetch(`/auth/checkuser?username=${this.username}`);
                const data = await response.json();
                this.usernameValid = data.exists;
            } catch (error) {
                console.error("Failed to check username:", error);
            }
        },
        async handleSubmit() {
            this.isSubmitting = true;

            try {
                const response = await fetch('/auth/authenticate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `username=${encodeURIComponent(this.username)}&password=${encodeURIComponent(this.password)}`,
                });

                const data = await response.json();

                // handle the response
                if (data.success) {
                    // successful login
                    this.passwordError = false;

                    // Redirect the user to the home page
                    window.location.href = "/home/";

                } else {
                    // login failed
                    this.passwordErrorMsg = data.message;
                    this.passwordError = true;
                }
            } catch (error) {
                console.error("Failed to submit:", error);
                alert('Error occurred while logging in. Please try again.');
            } finally {
                this.isSubmitting = false;
            }
        }
    },
};

const vueApp = createApp(app);
vueApp.mount('#app');
