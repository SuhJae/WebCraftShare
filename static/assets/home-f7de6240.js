import{o,a,b as e,d as E,r as s,l as j,h as x,t as i,e as k,u as y,f as d,F as C,m as A,_ as N,i as q,j as z,k as B}from"./XMarkIcon-24b34893.js";function F(S,l){return o(),a("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 24 24",fill:"currentColor","aria-hidden":"true"},[e("path",{"fill-rule":"evenodd",d:"M18.685 19.097A9.723 9.723 0 0021.75 12c0-5.385-4.365-9.75-9.75-9.75S2.25 6.615 2.25 12a9.723 9.723 0 003.065 7.097A9.716 9.716 0 0012 21.75a9.716 9.716 0 006.685-2.653zm-12.54-1.285A7.486 7.486 0 0112 15a7.486 7.486 0 015.855 2.812A8.224 8.224 0 0112 20.25a8.224 8.224 0 01-5.855-2.438zM15.75 9a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z","clip-rule":"evenodd"})])}const U={class:"bg-slate-200 bg-opacity-40 dark:bg-slate-950 dark:bg-opacity-40 shadow-sm py-3 px-6 backdrop-blur-md sticky top-0 z-50 border-b border-opacity-20 border-slate-400 dark:border-opacity-20 dark:border-slate-200"},V={class:"flex items-center justify-between mx-auto px-4 w-full"},W={class:"flex items-center space-x-2"},I={key:0,class:"h-10 w-auto",src:N,alt:"WebCraftShare Logo"},R={key:1,class:"h-10 w-auto",src:q,alt:"WebCraftShare Logo"},H=e("span",{class:"text-xl font-semibold hidden md:block"},"WebCraftShare",-1),$=e("span",{class:"text-xl font-semibold md:hidden"},"WCS",-1),O={class:"flex items-center space-x-4"},Y={class:"flex items-center space-x-4 md:flex hidden text-right",id:"navbarDropdown"},G={class:"text-gray-700 dark:text-white"},J={class:"font-semibold"},K={class:"text-emerald-500"},P=e("br",null,null,-1),Q={key:0,class:"glass-morphic-window absolute right-6 top-14 md:hidden",id:"smallScreenMenu"},X={class:"p-4 border-b border-opacity-20 border-slate-400 dark:border-opacity-20 dark:border-slate-200"},Z={class:"font-semibold"},ee={class:"text-emerald-500"},te=e("br",null,null,-1),se={key:0,class:"model fixed inset-0 flex items-start justify-center pt-20"},oe={class:"model__content p-6 glass-morphic-window w-96 absolute top-1/5 left-1/2 transform -translate-x-1/2"},ae={class:"model__header flex justify-between items-center mb-4"},le={class:"model__title text-2xl font-semibold"},ne={class:"model__body"},ie=["innerHTML"],re={key:0,class:"model__footer flex justify-end mt-4"},de={class:"max-w-screen-lg align-middle mx-auto"},ce=e("h1",null,"Test title",-1),ue=e("p",null,"Lorem ipsum, dolor sit amet consectetur adipisicing elit. Expedita adipisci laboriosam, sit, eos voluptatem error voluptate possimus quisquam aliquid numquam odio deserunt voluptates non ea praesentium ipsa exercitationem. Sint, ipsam.",-1),me=[ce,ue],he=E({__name:"home",setup(S){let l=null;const c=s(!1),L=s(""),u=s(!1),m=s(!1),h=s("Dialog title"),r=s('This is a <u>dialog</u> You can use it to display relevant information to the user. This is a <a href="https://google.com">URL</a>'),_=s(!1),p=s(!1),v=s("user@example.com"),b=s("user");function D(){c.value=!c.value}function f(t,w){h.value=t,r.value=w,m.value=!0}function n(){_.value||(m.value=!1,p.value=!1,h.value="",r.value="")}function g(){f("Logout","Are you sure you want to logout?"),p.value=!0}function M(){n(),_.value=!0,f("Returning to home","Successfully logged out");let t=3;l=window.setInterval(()=>{t-=.1,t=parseFloat(t.toFixed(1)),t<=0?(clearInterval(l),window.location.href="/"):r.value=`Successfully logged out!<br>Returning to <a herf="/">home</a> in ${t}s...`},100)}return window.addEventListener("keydown",t=>{t.key==="Escape"&&n()}),window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",t=>{u.value=t.matches}),window.addEventListener("load",()=>{u.value=window.matchMedia("(prefers-color-scheme: dark)").matches,L.value=window.location.origin}),j(()=>{l&&clearInterval(l)}),(t,w)=>(o(),a(C,null,[e("nav",U,[e("div",V,[e("div",W,[u.value?(o(),a("img",I)):(o(),a("img",R)),H,$]),e("div",O,[e("div",Y,[e("div",G,[e("span",J,[x("Signed in as "),e("span",K,i(b.value),1)]),P,e("small",null,i(v.value),1)]),e("button",{class:"red-scary-button",onClick:g},"Sign Out")]),e("button",{class:"md:hidden p-2 hover:backdrop-blur-sm hover:backdrop-opacity-30 hover:bg-slate-300 dark:hover:bg-slate-700 rounded-md",onClick:D},[k(y(F),{class:"h-6 w-6"})]),c.value?(o(),a("div",Q,[e("div",X,[e("span",Z,[x("Signed in as: "),e("span",ee,i(b.value),1)]),te,e("small",null,i(v.value),1)]),e("button",{class:"w-full text-left p-4 text-red-500 font-semibold hover:text-white hover:bg-red-500 rounded-b-lg",onClick:g}," Sign out ")])):d("",!0)])])]),m.value?(o(),a("div",se,[e("div",{class:"absolute inset-0 bg-white bg-opacity-50 dark:bg-black dark:bg-opacity-50 backdrop-blur-sm",onClick:n}),e("div",oe,[e("div",ae,[e("h2",le,i(h.value),1),_.value?d("",!0):(o(),a("button",{key:0,class:"model__close p-1 hover:bg-slate-200 dark:hover:bg-slate-600 rounded",onClick:n},[k(y(z),{class:"h-6 w-6"})]))]),e("div",ne,[e("div",{innerHTML:r.value},null,8,ie)]),p.value?(o(),a("div",re,[e("button",{class:"just-a-button",onClick:n},"Cancel"),e("button",{class:"red-scary-button ml-2",onClick:M},"Confirm")])):d("",!0)])])):d("",!0),e("div",de,[(o(),a(C,null,A(100,T=>e("div",{key:T,class:"p-4"},me)),64))])],64))}});B(he).mount("#app");
