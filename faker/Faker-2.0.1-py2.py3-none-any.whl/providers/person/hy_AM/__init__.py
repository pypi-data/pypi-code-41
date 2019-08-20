# coding=utf-8

from __future__ import unicode_literals
from .. import Provider as PersonProvider


class Provider(PersonProvider):
    formats_male = (
        '{{first_name_male}} {{last_name}}',
    )

    formats_female = (
        '{{first_name_female}} {{last_name}}',
    )

    formats = formats_male + formats_female

    # Source: https://en.wiktionary.org/wiki/Category:Armenian_male_given_names
    first_names_male = (
        'Սիմոն',
        'Ուիլյամ',
        'Ստեֆան',
        'Ռիչարդ',
        'Ֆիլիպ',
        'Ջոն',
        'Հովիկ',
        'Հենրի',
        'Ջորջ',
        'Գարրի',
        'Ֆելիքս',
        'Լևոն',
        'Դոմինիկ',
        'Դենիս',
        'Դանիել',
        'Կլոդ',
        'Քրիստոֆեր',
        'Չարլի',
        'Կարլ',
        'Բորիս',
        'Բեռնար',
        'Անդրեաս',
        'Ալեքսանդր',
        'Աբրահամ',
        'Աբել',
        'Ահարոն',
        'Օլեգ',
        'Փայլակ',
        'Ցոլակ',
        'Րաֆֆի',
        'Տարոն',
        'Վլադիմիր',
        'Վիկտոր',
        'Վահե',
        'Վախթանգ',
        'Վազգեն',
        'Ստեփան',
        'Սեյրան',
        'Սերգեյ',
        'Ռուդոլֆ',
        'Ռուբեն',
        'Ռոման',
        'Ռոբերտ',
        'Ռաֆայել',
        'Շահեն',
        'Նորայր',
        'Նշան',
        'Նարեկ',
        'Նաիրի',
        'Յուրի',
        'Մուրադ',
        'Մխիթար',
        'Մաքսիմ',
        'Մարկոս',
        'Մանվել',
        'Կարեն',
        'Էդուարդ',
        'Էդգար',
        'Զոհրաբ',
        'Գրիգոր',
        'Գոռ',
        'Գևորգ',
        'Գաբրիել',
        'Արման',
        'Արթուր',
        'Անդրանիկ',
        'Ալբերտ',
        'Ադամ',
        'Աբել',
        'Հովհաննես',
        'Աբիգ',
        'Ավետիք',
        'Ավետիս',
        'Աղասի',
        'Ազատ',
        'Հայկ',
        'Հայկազ',
        'Հակոբ',
        'Համազասպ',
        'Հմայակ',
        'Առաքել',
        'Արամ',
        'Արամազդ',
        'Արգամ',
        'Արգիշտի',
        'Արեգ',
        'Արիստակես',
        'Արմեն',
        'Արմենակ',
        'Արսեն',
        'Արտավազդ',
        'Արտակ',
        'Արտաշես',
        'Արտեմ',
        'Արտուր',
        'Արտուշ',
        'Հարություն',
        'Առուշան',
        'Արշավիր',
        'Արշակ',
        'Ատոմ',
        'Աշոտ',
        'Բաբկեն',
        'Բաղդասար',
        'Բաղիշ',
        'Բաղրամ',
        'Բագրատ',
        'Բարսեղ',
        'Բարխուդար',
        'Վահագն',
        'Վահան',
        'Վաղարշակ',
        'Վահրամ',
        'Վարուժան',
        'Վասակ',
        'Գագիկ',
        'Գալուստ',
        'Գարեգին',
        'Գառնիկ',
        'Գարսևան',
        'Գասպար',
        'Գեղամ',
        'Հրանտ',
        'Գուրգեն',
        'Դավիթ',
        'Դերենիկ',
        'Ջիվան',
        'Եղիշ',
        'Երվանդ',
        'Ժիրայր',
        'Զավեն',
        'Զորի',
        'Զոհրապ',
        'Կիկոս',
        'Կիրակոս',
        'Կորյուն',
        'Մամիկոն',
        'Մարգար',
        'Մհեր',
        'Մելքոն',
        'Մելքում',
        'Մեսրոպ',
        'Մեխակ',
        'Միհրան',
        'Մինաս',
        'Մուշեղ',
        'Ներսես',
        'Նուբար',
        'Օհան',
        'Փանոս',
        'Պարգև',
        'Պարթև',
        'Պարույր',
        'Պատվական',
        'Պետրոս',
        'Պողոս',
        'Սահակ',
        'Սաղաթել',
        'Սանասար',
        'Սարգիս',
        'Սասուն',
        'Սերոբ',
        'Սմբատ',
        'Սպարտակ',
        'Սուքիաս',
        'Սուրեն',
        'Թադևոս',
        'Թաթոս',
        'Թաթուլ',
        'Տիգրան',
        'Թորգոմ',
        'Թորոս',
        'Տրդատ',
        'Հունան',
        'Հուսիկ',
        'Խորեն',
        'Խոսրով',
        'Շավարշ',
        'Շմավոն',
    )

    # Source: https://en.wiktionary.org/wiki/Category:Armenian_female_given_names
    first_names_female = (
        'Ագապի',
        'Աիդա',
        'Ալեքսանդրա',
        'Ալինա',
        'Ալիսա',
        'Ալվարդ',
        'Ալլա',
        'Անիտա',
        'Ամալյա',
        'Անահիտ',
        'Անաստասիա',
        'Անժելա',
        'Անգելինա',
        'Անի',
        'Անյա',
        'Աննա',
        'Անտոնինա',
        'Անուշ',
        'Աստղիկ',
        'Արաքսյա',
        'Արևիկ',
        'Արմինե',
        'Արմենուհի',
        'Արփինե',
        'Բարբարա',
        'Բեթի',
        'Բելլա',
        'Բրիժիտ',
        'Բրիջիտ',
        'Գաբրիելլա',
        'Գայանե',
        'Գյուլնարա',
        'Գոհար',
        'Գրետա',
        'Դանիելլա',
        'Դիանա',
        'Դինա',
        'Ելենա',
        'Եվա',
        'Եվգինե',
        'Երանուհի',
        'Զարուհի',
        'Էլեն',
        'Էլիզա',
        'Էլինա',
        'Էմիլիա',
        'Էմմա',
        'Էրիկա',
        'Էվելինա',
        'Թագուհի',
        'Թամարա',
        'Թեհմինե',
        'Թերեզա',
        'Թինա',
        'Ժաքլին',
        'Ժաննա',
        'Իզաբելլա',
        'Ինգա',
        'Ինեսա',
        'Իննա',
        'Իրինա',
        'Լալա',
        'Լառա',
        'Լարիսա',
        'Լաուրա',
        'Լեյլա',
        'Լենա',
        'Լիա',
        'Լիանա',
        'Լիդա',
        'Լիզա',
        'Լիլիթ',
        'Լուսինե',
        'Լուիզա',
        'Ծովինար',
        'Կարինե',
        'Կարոլին',
        'Կասանդրա',
        'Կիրա',
        'Կլարա',
        'Հայկուհի',
        'Հասմիկ',
        'Հեղինե',
        'Հերմինե',
        'Հիլդա',
        'Հռիփսիմե',
        'Հրաչուհի',
        'Մագդա',
        'Մանե',
        'Մարգարիտա',
        'Մարթա',
        'Մարիամ',
        'Մարինե',
        'Մարիա',
        'Մարիաննա',
        'Մելանյա',
        'Մելինե',
        'Միլենա',
        'Մերի',
        'Մոնիկա',
        'Նազելի',
        'Նաիրա',
        'Նանա',
        'Նանե',
        'Նատաշա',
        'Նարե',
        'Նարինե',
        'Նելլի',
        'Նինա',
        'Նոննա',
        'Նորա',
        'Նվարդ',
        'Նունե',
        'Շահանե',
        'Շուշանիկ',
        'Պատրիսիա',
        'Ջեմմա',
        'Ջեյն',
        'Ջեսիկա',
        'Ջուլիետա',
        'Ռաիսա',
        'Ռեբեկա',
        'Ռիմա',
        'Ռիտա',
        'Ռուզան',
        'Սաթենիկ',
        'Սառա',
        'Սեդա',
        'Սեսիլիա',
        'Սիլվա',
        'Սիրարփի',
        'Սյուզաննա',
        'Սոնա',
        'Սոֆյա',
        'Սվետլանա',
        'Ստելլա',
        'Սուսաննա',
        'Վերոնիկա',
        'Վիկտորյա',
        'Վիոլետա',
        'Տաթևիկ',
        'Քիմ',
        'Քնարիկ',
        'Քրիստինե',
        'Օլգա',
        'Օվսաննա',
        'Օֆելյա',
        'Ֆլորա',
        'Ֆրիդա',
    )

    first_names = first_names_male + first_names_female

    # Source: https://en.wiktionary.org/wiki/Category:Armenian_surnames
    last_names = (
        'Աբազյան',
        'Աբաղյան',
        'Աբաղյանց',
        'Աբամելիքյան',
        'Աբաշյան',
        'Աբաջանյան',
        'Աբաջյան',
        'Աբասյան',
        'Աբգարյան',
        'Աբդալյան',
        'Աբդոյան',
        'Աբեթնակյան',
        'Աբելանց',
        'Աբելյան',
        'Աբեղյան',
        'Աբեշյան',
        'Աբեսալոմյանց',
        'Աբթեքյան',
        'Աբիսալոմյան',
        'Աբիսողոմոնյան',
        'Աբոյան',
        'Աբովյան',
        'Աբուջանյան',
        'Աբուսեֆյան',
        'Աբրահամյան',
        'Աբրոյան',
        'Ագիլյան',
        'Ագիշյան',
        'Ագլինցյան',
        'Ագշեհիրյան',
        'Ագոզյան',
        'Ագուլյան',
        'Ագուջյան',
        'Ագրալյան',
        'Ագրակլյան',
        'Ագրամազյան',
        'Ագրապյան',
        'Ագրիպասյան',
        'Ագրյան',
        'Ադաբաշյան',
        'Ադաթուրյան',
        'Ադալյան',
        'Ադամյան',
        'Ադամյանց',
        'Ադանալյան',
        'Ադանելյան',
        'Ադանյան',
        'Ադաջյան',
        'Ադելյան',
        'Ադեյան',
        'Ադիբեկ-Մելիքյան',
        'Ադիբեկյան',
        'Ադիգյոզալյան',
        'Ադիգոզյան',
        'Ադիլխանյան',
        'Ադիլյան',
        'Ադիխանյան',
        'Ադիմզալյան',
        'Ադիյան',
        'Ադիշյան',
        'Ադլխանյան',
        'Ադյան',
        'Ադոյան',
        'Ադոնց',
        'Ադուլյան',
        'Ադունց',
        'Ադրունի',
        'Ազաբյան',
        'Ազանյան',
        'Ազատիկյան',
        'Ազատխանյան',
        'Ազատյան',
        'Ազատյանց',
        'Ազարամյան',
        'Ազարբեկյան',
        'Ազարիկյան',
        'Ազարյան',
        'Ազարումյան',
        'Ազբեկյան',
        'Ազգալդյան',
        'Ազգալդրյան',
        'Ազգելդյան',
        'Ազգուլյան',
        'Ազդարյան',
        'Ազիզբեկյան',
        'Ազիզխանյան',
        'Ազիզյան',
        'Ազիլազյան',
        'Ազիկյան',
        'Ազիրյան',
        'Ազյան',
        'Ազնավուրյան',
        'Ազոյան',
        'Ազուլյան',
        'Ազրյան',
        'Ազրոյան',
        'Աթաբահյան',
        'Աթաբեկյան',
        'Աթաբեկյանց',
        'Աթագյուլյան',
        'Աթալարյան',
        'Աթալյան',
        'Աթալյանց',
        'Աթախանյան',
        'Աթամանյան',
        'Աթամյան',
        'Աթայան',
        'Աթանագինյան',
        'Աթանասյան',
        'Աթանեսյան',
        'Աթանոսյան',
        'Աթաշյան',
        'Աթաջյան',
        'Աթասյան',
        'Աթասունց',
        'Աթարբեկյան',
        'Աթարյան',
        'Աթաքյան',
        'Աթբաշյան',
        'Աթեճյան',
        'Աթեշյան',
        'Աթերզյան',
        'Աթինիզյան',
        'Աթինյան',
        'Աթլոյան',
        'Աթմաճյան',
        'Աթմաջյան',
        'Աթյան',
        'Աթոյան',
        'Աթոռակալյան',
        'Աթումյան',
        'Աթչյան',
        'Աթքյան',
        'Աժանջյան',
        'Աժդահարյան',
        'Աժդարյան',
        'Աժդերհանյան',
        'Աժտեհանյան',
        'Աժտերխանյան',
        'Աժտիկյան',
        'Ալաբաշյան',
        'Ալաբեկյան',
        'Ալաբերկյան',
        'Ալաբերճյան',
        'Ալագյոզյան',
        'Ալաջաջյան',
        'Ալավերդյան',
        'Ալեքսանյան',
        'Ալոյան',
        'Աղաբաբյան',
        'Աղաբեկյան',
        'Աղաջանյան',
        'Աղասյան',
        'Ամարյան',
        'Ամիրբեկյան',
        'Ամիրխանյան',
        'Այվազյան',
        'Անանյան',
        'Անդրեասյան',
        'Անղալադյան',
        'Անոփյան',
        'Անտոնյան',
        'Առաքելյան',
        'Առուստամյան',
        'Ասատրյան',
        'Ասլանյան',
        'Աստվածատրյան',
        'Ավագյան',
        'Ավդալյան',
        'Ավետիսյան',
        'Ավոյան',
        'Ավչյան',
        'Ատրյան',
        'Արեգյան',
        'Արեշյան',
        'Արզումանյան',
        'Արծրունի',
        'Բաբալյան',
        'Բաբաջանյան',
        'Բաբայան',
        'Բաբուջյան',
        'Բագրատյան',
        'Բագրատունի',
        'Բադալյան',
        'Բադալով',
        'Բադասյան',
        'Բադեյան',
        'Բադիկյան',
        'Բազեյան',
        'Բազունց',
        'Բակունց',
        'Բաղդասարյան',
        'Բարսեղյան',
        'Բեկզադյան',
        'Բեկզադով',
        'Բեկյան',
        'Բեկնազարյան',
        'Բեջանյան',
        'Բերբերյան',
        'Բոյաջյան',
        'Բոստանջյան',
        'Բունիաթյան',
        'Բուռնազյան',
        'Գաբոյան',
        'Գաբուզյան',
        'Գաբրիելյան',
        'Գալաչյան',
        'Գալստյան',
        'Գալդունց',
        'Գալֆայան',
        'Գալոյան',
        'Գասպարյան',
        'Գասպարով',
        'Գավալջյան',
        'Գարասեֆերյան',
        'Գերավետյան',
        'Գզիրյան',
        'Գիլոյան',
        'Գիմիշյան',
        'Գլեչյան',
        'Գյանջեցյան',
        'Գյուլնազարյան',
        'Գյումուշյան',
        'Գնունի',
        'Գրիգորյան',
        'Գուլաքսյան',
        'Գուլումյան',
        'Գևորգյան',
        'Դաբաղյան',
        'Դադալյան',
        'Դադասյան',
        'Դալլաքյան',
        'Դանիելյան',
        'Դարբինյան',
        'Դարչինյան',
        'Դեմուրյան',
        'Դևրիկյան',
        'Դիմաքսյան',
        'Դոդոխյան',
        'Դոլուխանյան',
        'Դոլուխանով',
        'Դոխոլյան',
        'Դոխոյան',
        'Դոխոյանց',
        'Դովլաթբեկյան',
        'Դովլաթյան',
        'Դուդուկչյան',
        'Դուզճակատչյան',
        'Դուվալյան',
        'Եգանյան',
        'Եգորյան',
        'Եղիազարյան',
        'Եղնուկյան',
        'Ենգիբարյան',
        'Ենգիբարով',
        'Ենգոյան',
        'Ենիգոմեշյան',
        'Ենոքյան',
        'Եսայան',
        'Երեմյան',
        'Երիբեկյան',
        'Երկանյան',
        'Եփրեմյան',
        'Զադոյան',
        'Զազյան',
        'Զանազանյան',
        'Զավրիյան',
        'Զավարյան',
        'Զատիկյան',
        'Զարգարյան',
        'Զարյան',
        'Զարուբյան',
        'Զաքարյան',
        'Զաքյան',
        'Զաքոյան',
        'Զելվեյան',
        'Զեյթունցյան',
        'Զեյնալյան',
        'Զոհրաբյան',
        'Զոլյան',
        'Զուռնաչյան',
        'Զուրաբյան',
        'Էլբակյան',
        'Էլոյան',
        'Էլչիբեկյան',
        'Էնֆիաջյան',
        'Էսկիբաշյան',
        'Ըրղաթբաշյան',
        'Թադևոսյան',
        'Թաթուլյան',
        'Թաթունց',
        'Թամազյան',
        'Թաշչյան',
        'Թարաքաջյան',
        'Թառայան',
        'Թերզյան',
        'Թեքեյան',
        'Թովմասյան',
        'Թորգոմյան',
        'Թորոսյան',
        'Թովուլջյան',
        'Թումանյան',
        'Թևոսյան',
        'Ժամագործյան',
        'Ժամկոչյան',
        'Իբրահիմբեկյան',
        'Իգիթբաշյան',
        'Իգիթխանյան',
        'Իգիթյան',
        'Իզմիրյան',
        'Իմաստունյան',
        'Իմեքչյան',
        'Իշլեմեճյան',
        'Իշխանյան',
        'Իշտոյան',
        'Իսաբեկյան',
        'Իսաբեկյանց',
        'Իսահակյան',
        'Իսկանդարյան',
        'Իսրայելյան',
        'Լազարյան',
        'Լազարյանց',
        'Լալայան',
        'Լալայանց',
        'Լամբարյան',
        'Լեմենցյան',
        'Լիպարիտյան',
        'Լպուտյան',
        'Լցկարյան',
        'Լուսպարոնյան',
        'Խազաբաշյան',
        'Խազխազյան',
        'Խալաֆյան',
        'Խալիկյան',
        'Խանբաբյան',
        'Խանզադյան',
        'Խաշմանյան',
        'Խաչատրյան',
        'Խաչատրյանց',
        'Խաչենց',
        'Խաչիկօղլյան',
        'Խառատյան',
        'Խեչանյան',
        'Խզմալյան',
        'Խլղաթյան',
        'Խնկոյան',
        'Խոդիկյան',
        'Խուդոյան',
        'Ծաղիկյան',
        'Ծառուկյան',
        'Ծատուրյան',
        'Ծերունյան',
        'Ծորմոտյան',
        'Ծպնեցյան',
        'Ծուռվիզյան',
        'Կաբակուլակյան',
        'Կաբաղյան',
        'Կաբասկալյան',
        'Կադարջյան',
        'Կալդրիկյան',
        'Կալենց',
        'Կալպակչյան',
        'Կամսարյան',
        'Կամսարյանց',
        'Կայֆեջյան',
        'Կաշեգործյան',
        'Կարագյան',
        'Կարախանյան',
        'Կարամանուկյան',
        'Կարապետյան',
        'Կարճիկյան',
        'Կետիկյան',
        'Կոթողյան',
        'Կոնդախչյան',
        'Կոշկակարյան',
        'Կոստանյան',
        'Կրպեյան',
        'Կույումջանյան',
        'Հալաբյան',
        'Հախվերդյան',
        'Հակոբյան',
        'Համբարձումյան',
        'Հայրապետյան',
        'Հայրբաբամյան',
        'Հայրիկյան',
        'Հատիկյան',
        'Հաջինյան',
        'Հարությունյան',
        'Հովասափյան',
        'Հովհաննիսյան',
        'Հովիվյան',
        'Հովսեփյան',
        'Հովսեփով',
        'Հուրդաջյան',
        'Ձավարյան',
        'Ձիթողցյան',
        'Ձիլֆուղարյան',
        'Ձկնորսյան',
        'Ձվակերյան',
        'Ղաբզիմալյան',
        'Ղազախեթյան',
        'Ղազանչյան',
        'Ղազարյան',
        'Ղազարով',
        'Ղազինյան',
        'Ղալդունց',
        'Ղալթախչյան',
        'Ղահրամանյան',
        'Ղամբարյան',
        'Ղայլունջյան',
        'Ղայֆեճյան',
        'Ղանդիլյան',
        'Ղասաբյան',
        'Ղասաբօղլյան',
        'Ղափլանյան',
        'Ղոլթաղչյան',
        'Ճալտիկյան',
        'Ճաղարյան',
        'Ճանճապանյան',
        'Ճանսուզյան',
        'Ճապաղջուրյան',
        'Ճգնավորյան',
        'Ճենեպերեքյան',
        'Ճիվասզյան',
        'Ճոճկանյան',
        'Ճուղուրյան',
        'Մադաթյան',
        'Մազմանյան',
        'Մանանդյան',
        'Մանուկյան',
        'Մանվելյան',
        'Մարաշյան',
        'Մարգարյան',
        'Մելիք-Աբրահամյան',
        'Մելիք-Ադամյան',
        'Մելիք-Ասլանյան',
        'Մելիք-Բարխուդարյան',
        'Մելիք-Օհանջանյան',
        'Մեհրաբյան',
        'Միկոյան',
        'Մինասբեկյան',
        'Մինասյան',
        'Միսակյան',
        'Միրզոյան',
        'Միրզոյանց',
        'Միքայելյան',
        'Մխիթարյան',
        'Մնացականյան',
        'Մշեցյան',
        'Մովսիսյան',
        'Մոսինյան',
        'Մսագործյան',
        'Մսրյան',
        'Մուշեղյան',
        'Մուշկամբարյան',
        'Մուսայելյան',
        'Մուրադյան',
        'Յաբլուկյան',
        'Յագուբյան',
        'Յազիչյան',
        'Յաղլիճյան',
        'Յոգուրթչյան',
        'Յուզբաշյան',
        'Յություճյան',
        'Նաբաթյան',
        'Նազարյան',
        'Նալբանդյան',
        'Նալչադյան',
        'Նախշքարյան',
        'Նահապետյան',
        'Ներկարարյան',
        'Ներսեսյան',
        'Ներսիսյան',
        'Նիկողոսյան',
        'Նշանյան',
        'Շաբոյան',
        'Շաբունց',
        'Շագոյան',
        'Շալավասյան',
        'Շահազիզյան',
        'Շահբազյան',
        'Շահինյան',
        'Շահինյանց',
        'Շահնազարյան',
        'Շարաբխանյան',
        'Շաքարյան',
        'Շաքրամանյան',
        'Շելունց',
        'Շուքուրյան',
        'Ոսկանյան',
        'Ոսկերչյան',
        'Չալիկյան',
        'Չալխիֆալակյան',
        'Չալոյան',
        'Չախմախչյան',
        'Չեմեդիկյան',
        'Չեպչյան',
        'Չեքիջյան',
        'Չիբուխչյան',
        'Չիլինգարյան',
        'Չիվչյան',
        'Չոբանյան',
        'Պալյան',
        'Պապայան',
        'Պապիկյան',
        'Պապոյան',
        'Պառավյան',
        'Պարոնիկյան',
        'Պարոնյան',
        'Պարոնյանց',
        'Պարսամյան',
        'Պերեճիկլյան',
        'Պետրոսյան',
        'Պետրոսյանց',
        'Պոզապալյան',
        'Պողոսյան',
        'Պողպատյան',
        'Պռոշյան',
        'Պստիկյան',
        'Ջալալբեկյան',
        'Ջանավարյան',
        'Ջանգիրյան',
        'Ջանիբեկյան',
        'Ջանջուղազյան',
        'Ջանփոլադյան',
        'Ջանունց',
        'Ջերեջյան',
        'Ջիգարխանյան',
        'Ջուլֆիղարյան',
        'Ռաշիդյան',
        'Ռասիմոսյան',
        'Ռևազյան',
        'Ռշտունի',
        'Ռոստոմյան',
        'Ռուբինյան',
        'Ռուստամյան',
        'Ռուստամյանց',
        'Սադոյան',
        'Սաթյան',
        'Սալբաշյան',
        'Սահակյան',
        'Սանթրոսյան',
        'Սանոյան',
        'Սարգսյան',
        'Սարխոյան',
        'Սարոյան',
        'Սիսոյան',
        'Սաֆարյան',
        'Սեմերջյան',
        'Սիմոնյան',
        'Սիրունյան',
        'Սոլախյան',
        'Սողոմոնյան',
        'Ստեփանյան',
        'Սրմաքեշյան',
        'Սուրմելյան',
        'Սուփրիկյան',
        'Սուքիասյան',
        'Վազիգեղցյան',
        'Վահանյան',
        'Վահունի',
        'Վանեցյան',
        'Վանյան',
        'Վարդապետյան',
        'Վարդերեսյան',
        'Վարոսյան',
        'Վարպետյան',
        'Վերանյան',
        'Վրացյան',
        'Տաճատյան',
        'Տասնապետյան',
        'Տարոնցյան',
        'Տեր-Գևորգյան',
        'Տեր-Հովհաննիսյան',
        'Տեր-Ղազարյան',
        'Տեր-Վահանյան',
        'Տոնոյան',
        'Տոպաջիկյան',
        'Տուղրեմաճյան',
        'Ցախկլորյան',
        'Ցիպլեցյան',
        'Ցոլակյան',
        'Ցրտատարյան',
        'Ուզանկիչյան',
        'Ուզունյան',
        'Ութմազյան',
        'Ուլիխանյան',
        'Ուլուբաբյան',
        'Ուստաբաշյան',
        'Ուրֆալյան',
        'Փալանդուզյան',
        'Փախչանյան',
        'Փահլևանյան',
        'Փամբուխչյան',
        'Փամբուկչյան',
        'Փայլաբազյան',
        'Փանոսյան',
        'Փաշայան',
        'Փաշինյան',
        'Փարաջանյան',
        'Փարաքեսիկյան',
        'Փարսադանյան',
        'Փափազյան',
        'Փիլիփոսյան',
        'Փոքրիկյան',
        'Քաթանասյան',
        'Քալանթարյան',
        'Քալաշյան',
        'Քաղցրիկյան',
        'Քարտաշյան',
        'Քափանակցյան',
        'Քեշիշյան',
        'Քեչօղլյան',
        'Քիլարջյան',
        'Քյոսայան',
        'Քոչարյան',
        'Քոչինյան',
        'Քրմոյան',
        'Քրքորյան',
        'Քուշքյան',
        'Օդյան',
        'Օզանյան',
        'Օզնեցյան',
        'Օհանյան',
        'Օրբելյան',
        'Ֆալյան',
        'Ֆահրադյան',
        'Ֆոլյան',
        'Ֆռանգյան',
        'Ֆրանգուլյան',
    )
