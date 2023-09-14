const app = Vue.createApp({
    data() {
        return {
            isSubmitting: false,
            isUploading: false,
            userName: '',
            domain: window.location.origin,
            filesValid: false,
            slug: '',
            slugWarning: null,
            slugMessage: '',
            slugValid: false,

            isDialogOpen: false,
            dialogTitle: '',
            dialogMessage: '',

            sites: [],
            isDeleting: false,

        };
    },
    computed: {
        slugAriaInvalid() {
            if (this.slugWarning === null) return undefined;
            return this.slugWarning.toString();
        },
    },
    methods: {
        async deleteSite(slug) {
            try {
                this.isDeleting = true;  // Set this flag to true to indicate the delete operation is in progress

                let response = await fetch('/api/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `slug=${encodeURIComponent(slug)}`
                });

                let data = await response.json();

                if (data.success) {
                    await this.fetchSites();  // Reload the list of sites
                    this.openDialog('👍 Success!', 'Your website, <del>' + slug + '</del> was deleted successfully! 💥')
                } else {
                    this.openDialog('😓 Error!', 'There was an error deleting your website. Please try again. ??')
                }
            } catch (error) {
                console.error('There was an error deleting the slug:', error);
                this.openDialog('😓 Error!', 'There was an error deleting your website. Please try again.')
            } finally {
                this.isDeleting = false;  // Reset the flag
            }
        },
        downloadSite(slug) {
            // Create an invisible form and submit it to initiate the download
            let form = document.createElement('form');
            form.method = 'POST';
            form.action = '/api/download';
            form.style.display = 'none';

            let input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'slug';
            input.value = slug;

            form.appendChild(input);
            document.body.appendChild(form);

            form.submit();

            document.body.removeChild(form);

            // reload the list of sites
            this.fetchSites();
        },

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
                    console.error(data.message);
                    this.openDialog('😓 Error!', 'There was an error logging you out. Please try again.')
                }
            } catch (error) {
                console.error('There was an error:', error);
                this.openDialog('😓 Error!', 'There was an error logging you out. Please try again.')
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

        async fetchSites() {
            this.sites = [];
            try {
                const response = await fetch('/api/getpages/', {
                    method: 'GET',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await response.json();
                if (data.pages) {
                    this.sites = data.pages.map(slug => ({slug, url: `${this.domain}/sites/${this.userName}/${slug}`}));
                } else {
                    console.error('Error fetching pages:', data.message);
                }
            } catch (error) {
                console.error('Error fetching user pages:', error);
            }
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
                this.openDialog('💻 Error!', 'Please select a folder to upload.')
                return;
            }

            const formData = new FormData();
            for (let i = 0; i < folderInput.files.length; i++) {
                // Skip dot files
                if (folderInput.files[i].name.startsWith('.')) {
                    continue;
                }

                // Use webkitRelativePath to preserve the directory structure.
                const path = folderInput.files[i].webkitRelativePath || folderInput.files[i].name;
                formData.append('file', folderInput.files[i], path);
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
                    await this.fetchSites();
                    this.url = this.domain + '/sites/' + this.userName + '/' + this.slug;
                    this.openDialog('👍 Success!', 'Your website was uploaded successfully! 🥳<br> <a href="' + this.url + '" target="_blank">' + this.url + '</a>')
                    this.$refs.folderInput.value = '';
                    this.slug = '';
                    this.filesValid = false;
                    this.slugWarning = null;
                    this.slugMessage = '';
                    this.slugValid = false;

                } else {
                    this.openDialog('🔥Error!', data.message || 'Upload failed. Please try again.')
                }
            } catch (error) {
                console.error('There was an error uploading the folder:', error);
                this.openDialog('😓 Error!', 'There was an error uploading your website. Please try again.')
            } finally {
                this.isUploading = false;
            }
        },
        async openDialog(title, message) {
            this.dialogTitle = title;
            this.dialogMessage = message;
            this.isDialogOpen = true;
        }
    },
    watch: {
        slug: "checkSlug"
    },
    mounted() {
        this.fetchUserName();
        this.fetchSites();
    }
});

app.mount('#app');
