import{Lt as e,Pt as t,a as n,s as r,t as i}from"./auth-DVMsQg9E.js";import{A as a,E as o,I as s,K as c,L as l,M as u,S as d,Z as f,c as p,g as m,gt as h,h as g,j as _,k as v,l as y,m as b,s as x,u as S,yt as C}from"./runtime-core.esm-bundler-CTn1umrH.js";import{S as w,f as T,l as E,p as D,v as O}from"./index-BweqMNhd.js";import{t as k}from"./inputtext-BO5bM1Bz.js";import{t as A}from"./password-CO5j00y4.js";var j=r.extend({name:`message`,style:`
    .p-message {
        display: grid;
        grid-template-rows: 1fr;
        border-radius: dt('message.border.radius');
        outline-width: dt('message.border.width');
        outline-style: solid;
    }

    .p-message-content-wrapper {
        min-height: 0;
    }

    .p-message-content {
        display: flex;
        align-items: center;
        padding: dt('message.content.padding');
        gap: dt('message.content.gap');
    }

    .p-message-close-button {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-inline-start: auto;
        overflow: hidden;
        position: relative;
        width: dt('message.close.button.width');
        height: dt('message.close.button.height');
        border-radius: dt('message.close.button.border.radius');
        background: transparent;
        transition:
            background dt('message.transition.duration'),
            color dt('message.transition.duration'),
            outline-color dt('message.transition.duration'),
            box-shadow dt('message.transition.duration'),
            opacity 0.3s;
        outline-color: transparent;
        color: inherit;
        padding: 0;
        border: none;
        cursor: pointer;
        user-select: none;
    }

    .p-message-close-button svg,
    .p-message-close-button i {
        font-size: dt('message.close.icon.size');
        width: dt('message.close.icon.size');
        height: dt('message.close.icon.size');
    }

    .p-message-close-button:focus-visible {
        outline-width: dt('message.close.button.focus.ring.width');
        outline-style: dt('message.close.button.focus.ring.style');
        outline-offset: dt('message.close.button.focus.ring.offset');
    }

    .p-message-info {
        background: dt('message.info.background');
        outline-color: dt('message.info.border.color');
        color: dt('message.info.color');
        box-shadow: dt('message.info.shadow');
    }

    .p-message-info .p-message-close-button:focus-visible {
        outline-color: dt('message.info.close.button.focus.ring.color');
        box-shadow: dt('message.info.close.button.focus.ring.shadow');
    }

    .p-message-info .p-message-close-button:hover {
        background: dt('message.info.close.button.hover.background');
    }

    .p-message-info.p-message-outlined {
        color: dt('message.info.outlined.color');
        outline-color: dt('message.info.outlined.border.color');
    }

    .p-message-info.p-message-simple {
        color: dt('message.info.simple.color');
    }

    .p-message-success {
        background: dt('message.success.background');
        outline-color: dt('message.success.border.color');
        color: dt('message.success.color');
        box-shadow: dt('message.success.shadow');
    }

    .p-message-success .p-message-close-button:focus-visible {
        outline-color: dt('message.success.close.button.focus.ring.color');
        box-shadow: dt('message.success.close.button.focus.ring.shadow');
    }

    .p-message-success .p-message-close-button:hover {
        background: dt('message.success.close.button.hover.background');
    }

    .p-message-success.p-message-outlined {
        color: dt('message.success.outlined.color');
        outline-color: dt('message.success.outlined.border.color');
    }

    .p-message-success.p-message-simple {
        color: dt('message.success.simple.color');
    }

    .p-message-warn {
        background: dt('message.warn.background');
        outline-color: dt('message.warn.border.color');
        color: dt('message.warn.color');
        box-shadow: dt('message.warn.shadow');
    }

    .p-message-warn .p-message-close-button:focus-visible {
        outline-color: dt('message.warn.close.button.focus.ring.color');
        box-shadow: dt('message.warn.close.button.focus.ring.shadow');
    }

    .p-message-warn .p-message-close-button:hover {
        background: dt('message.warn.close.button.hover.background');
    }

    .p-message-warn.p-message-outlined {
        color: dt('message.warn.outlined.color');
        outline-color: dt('message.warn.outlined.border.color');
    }

    .p-message-warn.p-message-simple {
        color: dt('message.warn.simple.color');
    }

    .p-message-error {
        background: dt('message.error.background');
        outline-color: dt('message.error.border.color');
        color: dt('message.error.color');
        box-shadow: dt('message.error.shadow');
    }

    .p-message-error .p-message-close-button:focus-visible {
        outline-color: dt('message.error.close.button.focus.ring.color');
        box-shadow: dt('message.error.close.button.focus.ring.shadow');
    }

    .p-message-error .p-message-close-button:hover {
        background: dt('message.error.close.button.hover.background');
    }

    .p-message-error.p-message-outlined {
        color: dt('message.error.outlined.color');
        outline-color: dt('message.error.outlined.border.color');
    }

    .p-message-error.p-message-simple {
        color: dt('message.error.simple.color');
    }

    .p-message-secondary {
        background: dt('message.secondary.background');
        outline-color: dt('message.secondary.border.color');
        color: dt('message.secondary.color');
        box-shadow: dt('message.secondary.shadow');
    }

    .p-message-secondary .p-message-close-button:focus-visible {
        outline-color: dt('message.secondary.close.button.focus.ring.color');
        box-shadow: dt('message.secondary.close.button.focus.ring.shadow');
    }

    .p-message-secondary .p-message-close-button:hover {
        background: dt('message.secondary.close.button.hover.background');
    }

    .p-message-secondary.p-message-outlined {
        color: dt('message.secondary.outlined.color');
        outline-color: dt('message.secondary.outlined.border.color');
    }

    .p-message-secondary.p-message-simple {
        color: dt('message.secondary.simple.color');
    }

    .p-message-contrast {
        background: dt('message.contrast.background');
        outline-color: dt('message.contrast.border.color');
        color: dt('message.contrast.color');
        box-shadow: dt('message.contrast.shadow');
    }

    .p-message-contrast .p-message-close-button:focus-visible {
        outline-color: dt('message.contrast.close.button.focus.ring.color');
        box-shadow: dt('message.contrast.close.button.focus.ring.shadow');
    }

    .p-message-contrast .p-message-close-button:hover {
        background: dt('message.contrast.close.button.hover.background');
    }

    .p-message-contrast.p-message-outlined {
        color: dt('message.contrast.outlined.color');
        outline-color: dt('message.contrast.outlined.border.color');
    }

    .p-message-contrast.p-message-simple {
        color: dt('message.contrast.simple.color');
    }

    .p-message-text {
        font-size: dt('message.text.font.size');
        font-weight: dt('message.text.font.weight');
    }

    .p-message-icon {
        display: inline-flex;
    }

    .p-message-icon,
    .p-message-icon svg,
    .p-message-icon i {
        flex-shrink: 0;
        font-size: dt('message.icon.size');
        width: dt('message.icon.size');
        height: dt('message.icon.size');
    }

    .p-message-sm .p-message-content {
        padding: dt('message.content.sm.padding');
    }

    .p-message-sm .p-message-text {
        font-size: dt('message.text.sm.font.size');
    }

    .p-message-sm .p-message-icon,
    .p-message-sm .p-message-icon svg,
    .p-message-sm .p-message-icon i {
        font-size: dt('message.icon.sm.size');
        width: dt('message.icon.sm.size');
        height: dt('message.icon.sm.size');
    }

    .p-message-sm .p-message-close-button svg,
    .p-message-sm .p-message-close-button i {
        width: dt('message.close.icon.sm.size');
        height: dt('message.close.icon.sm.size');
    }

    .p-message-lg .p-message-content {
        padding: dt('message.content.lg.padding');
    }

    .p-message-lg .p-message-text {
        font-size: dt('message.text.lg.font.size');
    }

    .p-message-lg .p-message-icon,
    .p-message-lg .p-message-icon svg,
    .p-message-lg .p-message-icon i {
        font-size: dt('message.icon.lg.size');
        width: dt('message.icon.lg.size');
        height: dt('message.icon.lg.size');
    }

    .p-message-lg .p-message-close-button svg,
    .p-message-lg .p-message-close-button i {
        font-size: dt('message.close.icon.lg.size');
        width: dt('message.close.icon.lg.size');
        height: dt('message.close.icon.lg.size');
    }

    .p-message-outlined {
        background: transparent;
        outline-width: dt('message.outlined.border.width');
    }

    .p-message-simple {
        background: transparent;
        outline-color: transparent;
        box-shadow: none;
    }

    .p-message-simple .p-message-content {
        padding: dt('message.simple.content.padding');
    }

    .p-message-outlined .p-message-close-button:hover,
    .p-message-simple .p-message-close-button:hover {
        background: transparent;
    }

    .p-message-enter-active {
        animation: p-animate-message-enter 0.3s ease-out forwards;
        overflow: hidden;
    }

    .p-message-leave-active {
        animation: p-animate-message-leave 0.15s ease-in forwards;
        overflow: hidden;
    }

    @keyframes p-animate-message-enter {
        from {
            opacity: 0;
            grid-template-rows: 0fr;
        }
        to {
            opacity: 1;
            grid-template-rows: 1fr;
        }
    }

    @keyframes p-animate-message-leave {
        from {
            opacity: 1;
            grid-template-rows: 1fr;
        }
        to {
            opacity: 0;
            margin: 0;
            grid-template-rows: 0fr;
        }
    }
`,classes:{root:function(e){var t=e.props;return[`p-message p-component p-message-`+t.severity,{"p-message-outlined":t.variant===`outlined`,"p-message-simple":t.variant===`simple`,"p-message-sm":t.size===`small`,"p-message-lg":t.size===`large`}]},contentWrapper:`p-message-content-wrapper`,content:`p-message-content`,icon:`p-message-icon`,text:`p-message-text`,closeButton:`p-message-close-button`,closeIcon:`p-message-close-icon`}}),M={name:`BaseMessage`,extends:n,props:{severity:{type:String,default:`info`},closable:{type:Boolean,default:!1},life:{type:Number,default:null},icon:{type:String,default:void 0},closeIcon:{type:String,default:void 0},closeButtonProps:{type:null,default:null},size:{type:String,default:null},variant:{type:String,default:null}},style:j,provide:function(){return{$pcMessage:this,$parentInstance:this}}};function N(e){"@babel/helpers - typeof";return N=typeof Symbol==`function`&&typeof Symbol.iterator==`symbol`?function(e){return typeof e}:function(e){return e&&typeof Symbol==`function`&&e.constructor===Symbol&&e!==Symbol.prototype?`symbol`:typeof e},N(e)}function P(e,t,n){return(t=F(t))in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function F(e){var t=I(e,`string`);return N(t)==`symbol`?t:t+``}function I(e,t){if(N(e)!=`object`||!e)return e;var n=e[Symbol.toPrimitive];if(n!==void 0){var r=n.call(e,t);if(N(r)!=`object`)return r;throw TypeError(`@@toPrimitive must return a primitive value.`)}return(t===`string`?String:Number)(e)}var L={name:`Message`,extends:M,inheritAttrs:!1,emits:[`close`,`life-end`],timeout:null,data:function(){return{visible:!0}},mounted:function(){var e=this;this.life&&setTimeout(function(){e.visible=!1,e.$emit(`life-end`)},this.life)},methods:{close:function(e){this.visible=!1,this.$emit(`close`,e)}},computed:{closeAriaLabel:function(){return this.$primevue.config.locale.aria?this.$primevue.config.locale.aria.close:void 0},dataP:function(){return t(P(P({outlined:this.variant===`outlined`,simple:this.variant===`simple`},this.severity,this.severity),this.size,this.size))}},directives:{ripple:T},components:{Times:D}};function R(e){"@babel/helpers - typeof";return R=typeof Symbol==`function`&&typeof Symbol.iterator==`symbol`?function(e){return typeof e}:function(e){return e&&typeof Symbol==`function`&&e.constructor===Symbol&&e!==Symbol.prototype?`symbol`:typeof e},R(e)}function z(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter(function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable})),n.push.apply(n,r)}return n}function B(e){for(var t=1;t<arguments.length;t++){var n=arguments[t]==null?{}:arguments[t];t%2?z(Object(n),!0).forEach(function(t){V(e,t,n[t])}):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):z(Object(n)).forEach(function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))})}return e}function V(e,t,n){return(t=H(t))in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function H(e){var t=U(e,`string`);return R(t)==`symbol`?t:t+``}function U(e,t){if(R(e)!=`object`||!e)return e;var n=e[Symbol.toPrimitive];if(n!==void 0){var r=n.call(e,t);if(R(r)!=`object`)return r;throw TypeError(`@@toPrimitive must return a primitive value.`)}return(t===`string`?String:Number)(e)}var W=[`data-p`],G=[`data-p`],K=[`data-p`],q=[`aria-label`,`data-p`],J=[`data-p`];function Y(e,t,n,r,i,c){var f=a(`Times`),m=_(`ripple`);return o(),p(O,d({name:`p-message`,appear:``},e.ptm(`transition`)),{default:s(function(){return[i.visible?(o(),S(`div`,d({key:0,class:e.cx(`root`),role:`alert`,"aria-live":`assertive`,"aria-atomic":`true`,"data-p":c.dataP},e.ptmi(`root`)),[x(`div`,d({class:e.cx(`contentWrapper`)},e.ptm(`contentWrapper`)),[e.$slots.container?v(e.$slots,`container`,{closeCallback:c.close},void 0,void 0,0):(o(),S(`div`,d({key:1,class:e.cx(`content`),"data-p":c.dataP},e.ptm(`content`)),[v(e.$slots,`icon`,{class:h(e.cx(`icon`))},function(){return[(o(),p(u(e.icon?`span`:null),d({class:[e.cx(`icon`),e.icon],"data-p":c.dataP},e.ptm(`icon`)),null,16,[`class`,`data-p`]))]}),e.$slots.default?(o(),S(`div`,d({key:0,class:e.cx(`text`),"data-p":c.dataP},e.ptm(`text`)),[v(e.$slots,`default`)],16,K)):y(``,!0),e.closable?l((o(),S(`button`,d({key:1,class:e.cx(`closeButton`),"aria-label":c.closeAriaLabel,type:`button`,onClick:t[0]||=function(e){return c.close(e)},"data-p":c.dataP},B(B({},e.closeButtonProps),e.ptm(`closeButton`))),[v(e.$slots,`closeicon`,{},function(){return[e.closeIcon?(o(),S(`i`,d({key:0,class:[e.cx(`closeIcon`),e.closeIcon],"data-p":c.dataP},e.ptm(`closeIcon`)),null,16,J)):(o(),p(f,d({key:1,class:[e.cx(`closeIcon`),e.closeIcon],"data-p":c.dataP},e.ptm(`closeIcon`)),null,16,[`class`,`data-p`]))]})],16,q)),[[m]]):y(``,!0)],16,G))],16)],16,W)):y(``,!0)]}),_:3},16)}L.render=Y;var X={class:`flex items-center justify-center min-h-screen bg-gray-50`},Z={class:`w-full max-w-md p-6 bg-white rounded-xl shadow-md`},Q={class:`flex flex-col gap-2`},$={class:`flex flex-col gap-2`},ee={class:`flex flex-col gap-2`},te={class:`flex flex-col gap-2`},ne={class:`text-center mt-6 text-sm`},re=m({__name:`RegisterView`,setup(t){let n=e(),r=i(),l=c(``),u=c(``),d=c(``),m=c(``),h=c(!1),_=c(``),v=async()=>{if(!l.value||!u.value||!d.value){_.value=`กรุณากรอกข้อมูลให้ครบถ้วน`;return}if(d.value!==m.value){_.value=`รหัสผ่านไม่ตรงกัน`;return}h.value=!0,_.value=``;try{await r.register({username:l.value,email:u.value,password:d.value})?n.push({name:`login`,query:{registered:`true`}}):_.value=r.error||`สมัครสมาชิกไม่สำเร็จ`}catch(e){_.value=e.message||`เกิดข้อผิดพลาดในการเชื่อมต่อ`}finally{h.value=!1}};return(e,t)=>{let n=a(`router-link`);return o(),S(`div`,X,[x(`div`,Z,[t[10]||=x(`div`,{class:`text-center mb-6`},[x(`h1`,{class:`text-2xl font-bold text-primary`},`สมัครสมาชิก`),x(`p`,{class:`text-gray-500 mt-2`},`Lunch Expense Tracker`)],-1),_.value?(o(),p(f(L),{key:0,severity:`error`,closable:!1,class:`mb-4`},{default:s(()=>[b(C(_.value),1)]),_:1})):y(``,!0),x(`form`,{onSubmit:w(v,[`prevent`]),class:`flex flex-col gap-4`},[x(`div`,Q,[t[4]||=x(`label`,{for:`username`},`ชื่อผู้ใช้`,-1),g(f(k),{id:`username`,modelValue:l.value,"onUpdate:modelValue":t[0]||=e=>l.value=e},null,8,[`modelValue`])]),x(`div`,$,[t[5]||=x(`label`,{for:`email`},`อีเมล`,-1),g(f(k),{id:`email`,type:`email`,modelValue:u.value,"onUpdate:modelValue":t[1]||=e=>u.value=e},null,8,[`modelValue`])]),x(`div`,ee,[t[6]||=x(`label`,{for:`password`},`รหัสผ่าน`,-1),g(f(A),{id:`password`,modelValue:d.value,"onUpdate:modelValue":t[2]||=e=>d.value=e,toggleMask:``},null,8,[`modelValue`])]),x(`div`,te,[t[7]||=x(`label`,{for:`confirmPassword`},`ยืนยันรหัสผ่าน`,-1),g(f(A),{id:`confirmPassword`,modelValue:m.value,"onUpdate:modelValue":t[3]||=e=>m.value=e,feedback:!1,toggleMask:``},null,8,[`modelValue`])]),g(f(E),{type:`submit`,label:`สมัครสมาชิก`,loading:h.value,class:`mt-4`},null,8,[`loading`])],32),x(`div`,ne,[t[9]||=b(` มีบัญชีอยู่แล้ว? `,-1),g(n,{to:`/login`,class:`text-primary font-semibold hover:underline`},{default:s(()=>[...t[8]||=[b(`เข้าสู่ระบบ`,-1)]]),_:1})])])])}}});export{re as default};