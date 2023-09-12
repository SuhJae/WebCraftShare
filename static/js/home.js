const app = Vue.createApp({
    data() {
        return {
            isSubmitting: false,
            isUploading: false,
            userName: '',
            filesValid: false,
            slug: '',
            slugWarning: null,
            slugMessage: '',
            slugValid: false
        };
    },
    computed: {
        slugAriaInvalid() {
            if (this.slugWarning === null) return undefined;
            return this.slugWarning.toString();
        },
    },
    methods: {
        async logout() {
            this.isSubmitting = true;
            try {
                let response = await fetch('/api/logout/', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                let data = await response.json();

                if (data.success) {
                    window.location.href = '/';
                } else {
                    alert('Logout failed. Please try again.');
                }
            } catch (error) {
                console.error('There was an error:', error);
                alert('An error occurred. Please try again.');
            } finally {
                this.isSubmitting = false;
            }
        },
        async fetchUserName() {
            try {
                let response = await fetch('/api/userinfo/', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                let data = await response.json();

                if (data.username) {
                    this.userName = data.username;
                } else {
                    console.error(data.message);
                }
            } catch (error) {
                console.error('There was an error fetching the username:', error);
            }
        },
        checkFiles(event) {
            const files = event.target.files;
            let hasIndexHtml = false;

            for (let i = 0; i < files.length; i++) {
                // Check if any file's path (or name for non-WebKit browsers) ends with 'index.html'
                if (files[i].webkitRelativePath.endsWith('index.html') || files[i].name === 'index.html') {
                    hasIndexHtml = true;
                    break;
                }
            }

            this.filesValid = hasIndexHtml;
        },
        async checkSlug() {
            if (!this.slug) {
                this.slugWarning = null;
                return;
            }
            try {


                if (!/^[a-zA-Z0-9-]+$/.test(this.slug)) {
                    this.slugWarning = true;
                    this.slugValid = false;
                    this.slugMessage = "Slug can only contain letters, numbers, and dashes!";
                } else {
                    const response = await fetch('/api/checkslug', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        body: `checkslug=${encodeURIComponent(this.slug)}`
                    });
                    const data = await response.json();

                    if (data.exists) {
                        this.slugWarning = true;
                        this.slugValid = false;
                        this.slugMessage = "Slug already exists. Please choose another.";
                    } else {
                        this.slugWarning = false
                        this.slugValid = true;
                        this.slugMessage = "Good to go!";
                    }
                }
            } catch (error) {
                console.error('There was an error checking the slug:', error);
            }
        },
        async uploadFolder() {
            const folderInput = this.$refs.folderInput;

            if (!folderInput.files.length) {
                alert('Please select a folder to upload.');
                return;
            }

            const formData = new FormData();
            for (let i = 0; i < folderInput.files.length; i++) {
                formData.append('file', folderInput.files[i]);
            }
            formData.append('slug', this.slug);

            this.isUploading = true;

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    alert('Folder uploaded successfully!');
                } else {
                    alert(data.message || 'Upload failed. Please try again.');
                }
            } catch (error) {
                console.error('There was an error uploading the folder:', error);
                alert('An error occurred. Please try again.');
            } finally {
                this.isUploading = false;
            }
        }
    },
    watch: {
        slug: "checkSlug"
    },
    mounted() {
        this.fetchUserName();
    }
});

app.mount('#app');
