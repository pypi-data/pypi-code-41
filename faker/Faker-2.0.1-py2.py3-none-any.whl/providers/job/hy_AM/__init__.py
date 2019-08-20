# coding=utf-8

from __future__ import unicode_literals
from .. import Provider as BaseProvider


class Provider(BaseProvider):
    jobs = (
        "Ակադեմիական գրադարանավար",
        "Հաշվապահ",
        "Դերասան",
        "Ասեղնաբույժ",
        "Ադմինիստրատոր",
        "Ավիացիոն ինժեներ",
        "Գյուղատնտեսական խորհրդատու",
        "Գյուղատնտեսական տեխնիկ",
        "Օդային երթևեկության վերահսկիչ",
        "Ավիաուղիների օդաչու",
        "Անիմատոր",
        "Հնագետ",
        "Ճարտարապետ",
        "Ճարտարապետական տեխնոլոգ",
        "Արխիվարիուս",
        "Զինված ուժերի տեխնիկական սպասարկող",
        "Զինված ուժերի ուսուցման և կրթության սպա",
        "Արվեստի պատկերասրահի կառավարիչ",
        "Արվեստագետ",
        "Դոցենտ",
        "Աստղագետ",
        "Աուդիո գիտնական",
        "Բանկիր",
        "Կենսաքիմիկոս",
        "Կենսաբժշկական ինժեներ",
        "Կենսաբժշկական գիտնական",
        "Պարտատոմսերի վաճառող",
        "Գրավաճառ",
        "Շինհրապարակի տեսուչ",
        "Շինությունների սպասարկման ինժեներ",
        "Սպասարկման կենտրոնի մենեջեր",
        "Օպերատոր",
        "Քարտեզագրիչ",
        "Քեյթերինգի մենեջեր",
        "Կերամիկայի դիզայներ",
        "Քիմիական ինժեներ",
        "Քիմիկոս",
        "Գլխավոր գործադիր տնօրեն",
        "Գլխավոր ֆինանսական տնօրեն",
        "Գլխավոր մարքեթինգային պատասխանատու",
        "Անձնակազմի ղեկավար",
        "Գործադիր տնօրեն",
        "Գլխավոր ռազմավարության պատասխանատու",
        "Գլխավոր տեխնոլոգիաների պատասխանատու",
        "Մանկական հոգեթերապևտ",
        "Կիրոպրատոր",
        "Քաղաքացիական ինժեներ",
        "Քաղաքացիական ծառայության վարչարար",
        "Կլինիկական կենսաքիմիկոս",
        "Կլինիկական ցիտոգենիկիստ",
        "Կլինիկական մոլեկուլային գենետիկ",
        "Կլինիկական հոգեբան",
        "Կոմերցիոն արվեստի պատկերասրահի ղեկավար",
        "Կապի ինժեներ",
        "Ընկերության քարտուղար",
        "Համակարգչային խաղեր մշակող",
        "Կոնֆերանսի կենտրոնի ղեկավար",
        "Կապալառու",
        "Կորպորատիվ ներդրումային բանկիր",
        "Կորպորատիվ գանձապահ",
        "Խորհրդատու հոգեբան",
        "Խորհրդատու",
        "Կուրատոր",
        "Հաճախորդների սպասարկման կառավարիչ",
        "Պարող",
        "Տվյալների մշակման մենեջեր",
        "Տվյալների գիտնական",
        "Տվյալների շտեմարանի կառավարիչ",
        "Դիլեր",
        "Ատամնաբույժ",
        "Վիտրաժների դիզայներ",
        "Կերամիկայի դիզայներ",
        "Ցուցահանդեսի դիզայներ",
        "Ոճաբան",
        "Կահույքի դիզայներ",
        "Գրաֆիկական դիզայներ",
        "Արդյունաբերական դիզայներ",
        "Ինտերիերի դիզայներ",
        "Զարդերի դիզայներ",
        "Մուլտիմեդիա դիզայներ",
        "Ֆիլմի դիզայներ",
        "Տեքստիլ դիզայներ",
        "Բնապահպան",
        "Տնտեսագետ",
        "Կրթական հոգեբան",
        "Էլեկտրատեխնիկ",
        "Էլեկտրոնիկայի ինժեներ",
        "Ավիացիոն ինժեներ",
        "Գյուղատնտեսական ինժեներ",
        "Ավտոմեքենայի ինժեներ",
        "Կենսաբժշկական ինժեներ",
        "Շինությունների սպասարկման ինժեներ",
        "Քիմիական ինժեներ",
        "Քաղաքացիական ինժեներ",
        "Կապի ինժեներ",
        "Հորատման ինժեներ",
        "Արտադրության համակարգերի ինժեներ",
        "Հանքարդյունաբերության ինժեներ",
        "Նավթային ինժեներ",
        "Երկրաբանական  ինժեներ",
        "Բնապահպանական խորհրդատու",
        "Բաժնետոմսերի վաճառող",
        "Էրգոնոմիստ",
        "Անշարժ գույքի գործակալ",
        "Միջոցառումների կազմակերպիչ",
        "Ցուցահանդեսի դիզայներ",
        "Դաշտային սեյսմոլոգ",
        "Ֆինանսական խորհրդատու",
        "Ֆինանսական վերահսկիչ",
        "Ֆինանսական մենեջեր",
        "Ֆինանսական պլանավորող",
        "Ֆինանսական ռիսկի վերլուծաբան",
        "Նկարիչ",
        "Հրշեջ",
        "Ֆիտնես կենտրոնի ղեկավար",
        "Սննդի տեխնոլոգ",
        "Դատական հոգեբան",
        "Դատաբժշկական գիտնական",
        "Տեքստիլ տեխնոլոգ",
        "Մոլեկուլային գենետիկ",
        "Երկրաբան",
        "Ապակեգործ",
        "Հեմատոլոգ",
        "Առողջության և անվտանգության հարցերով խորհրդատու",
        "Առողջապահության և անվտանգության տեսուչ",
        "Ֆիզիկոս",
        "Առողջության խթանման մասնագետ",
        "Առողջապահական ծառայությունների ղեկավար",
        "Հերտոլոգ",
        "Բարձրագույն կրթության կարիերայի խորհրդատու",
        "Պատմական շենքերի պահպանման մասնագետ",
        "Այգեգործության խորհրդատու",
        "Այգեգործ",
        "Հիվանդանոցի բժիշկ",
        "Հյուրանոցի կառավարիչ",
        "Մարդկային ռեսուրսների մասնագետ",
        "Հիդրոէկոլոգ",
        "Հիդրոգրաֆիկ հետազոտող",
        "Հիդրոլոգ",
        "Իմունոլոգ",
        "Տեղեկատվական աշխատող",
        "Տեղեկատվական համակարգերի կառավարիչ",
        "Ապահովագրության հաշվի կառավարիչ",
        "Ապահովագրական բրոքեր",
        "Ապահովագրական ռիսկերի հետազոտող",
        "Միջազգային օգնության աշխատող",
        "Թարգմանիչ",
        "Ներդրումային վերլուծաբան",
        "Ներդրումային բանկիր",
        "ՏՏ խորհրդատու",
        "ՏՏ վաճառքի մասնագետ",
        "Լրագրող",
        "Լանդշաֆտի ճարտարապետ",
        "Իրավաբան",
        "Փաստաբան",
        "Դասախոս",
        "Իրավական քարտուղար",
        "Ժամանցի կենտրոնի կառավարիչ",
        "Բառարանագիր",
        "Գրադարանավար",
        "Լուսավորման տեխնիկ",
        "Լոբբիստ",
        "Լոգիստիկայի և բաշխման մենեջեր",
        "Ամսագրի լրագրող",
        "Տեխնիկական սպասարկման մասնագետ",
        "Կառավարման խորհրդատու",
        "Արտադրության համակարգերի ինժեներ",
        "Շուկայի հետազոտող",
        "Մեխանիկական ինժեներ",
        "Հոգեկան առողջության բուժքույր",
        "Մետաղագործ",
        "Միկրոբիոլոգ",
        "Մանկաբարձուհի",
        "Հանքանյութերի հետազոտող",
        "Հանքարդյունաբերող",
        "Մուլտիմեդիայի ծրագրավորող",
        "Մուլտիմեդիայի մասնագետ",
        "Երաժշտության դասախոս",
        "Երաժիշտ",
        "Ցանցային ինժեներ",
        "Նյարդավիրաբույժ",
        "Բուժքույր",
        "Գրասենյակի մենեջեր",
        "Ուռուցքաբան",
        "Ակնաբույժ",
        "Օպտոմետրիստ",
        "Օրթոպիստ",
        "Օստեոպաթ",
        "Մանկական բուժքույր",
        "Պարամեդիկ",
        "Ուղևորափոխադրումների մենեջեր",
        "Արտոնագրային հավատարմատար",
        "Պաթոլոգ",
        "Անձնական օգնական",
        "Դեղագործ",
        "Դեղագետ",
        "Լուսանկարիչ",
        "Ֆիզիոլոգ",
        "Ֆիզիոթերապևտ",
        "Ֆիտոթերապևտ",
        "Գենետիկ",
        "Պոդիոնիստ",
        "Ոստիկան",
        "Պրոդյուսեր",
        "Ապրանքի դիզայներ",
        "Արտադրանքի մենեջեր",
        "Ծրագրավորող",
        "Սրբագրիչ",
        "Հոգեբույժ",
        "Հոգեբան",
        "Հոգեթերապևտ",
        "Գնումների մենեջեր",
        "Որակի մենեջեր",
        "Ռադիոլոգ",
        "Պահակ",
        "Գիտաշխատող",
        "Ռեստորանի կառավարիչ",
        "Գիտական լաբորատորիայի տեխնիկ",
        "Դատաբժիշկ",
        "Հարկային տեսուչ",
        "Սոցիալական աշխատող",
        "Հավատարմատար",
        "Ձայնային տեխնիկ",
        "Խոսքի և լեզվի թերապևտ",
        "Մարզիչ",
        "Սպորտային թերապևտ",
        "Վիճակագրագետ",
        "Վիրաբույժ",
        "Բժիշկ",
        "Համակարգերի վերլուծաբան",
        "Հարկային խորհրդատու",
        "Ուսուցիչ",
        "Թերապևտիկ ռադիոլոգ",
        "Թերապևտ",
        "Տուր մենեջեր",
        "Թոքիկոլոգ",
        "Թարգմանիչ",
        "Տրանսպորտի պլանավորող",
        "Անասնաբույժ",
        "Պահեստապետ",
        "Թափոնների կառավարման պատասխանատու",
        "Ջրի որակի գիտնական",
        "Վեբ դիզայներ",
        "Գրող",
    )
