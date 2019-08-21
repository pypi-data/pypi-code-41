from buiz.question import question
print("Bienvenido al Quiz\n\nIntroduzca la letra correcta\nNOTA: Si introduce la letra incorrecta la respuesta sera nula.")

question_prompts = [
    "\n1. ¿En que continente esta El Ecuador?\n(a) Asia\n(b) America\n(c) Europa\n\n",
    "2. ¿Cual es el oceano mas grande?\n(a) Oceano Pacifico\n(b) Oceano Atlantico\n(c) Oceano Indico\n\n",
    "3. ¿Cual es el pais mas grande del mundo?\n(a) China\n(b) Estados Unidos\n(c) Rusia\n\n",
    "4. ¿Cual es la principal ciudad de los rascacielos?\n(a) Tokyo\n(b) Hong Kong\n(c) Nueva York\n\n",
    "5. ¿Quien gano el mundial de 2014?\n(a) Alemania\n(b) Francia\n(c) Argentina\n\n",
    "6. ¿Cual es el metal mas caro del mundo?\n(a) Oro\n(a) Platino\n(c) Rodio\n\n",
    "7. ¿Cual es la quinta provincia de panama?\n(a) Herrera\n(b) Darien\n(c) Colon\n\n",
    "8. ¿Quien escribio el himno nacional de Panama?\n(a) Jeronimo de la Ossa\n(b) Santos jorge amatrian\n(c) Manuel Amador Guerrero\n\n",
    "9. ¿Quien fue el primer presidente de Panama?\n(a) Dr. Manuel Amador Guerrero\n(b) Torrijos Carter\n(c) Jeronimo de Ossa\n\n",
    "10. ¿En que año fue inagurado el Canal de Panama?\n(a) 1999\n(b) 1948\n(c) 1914\n\n",
]

questions = [
    question(question_prompts[0],"b"),
    question(question_prompts[1],"a"),
    question(question_prompts[2],"c"),
    question(question_prompts[3],"b"),
    question(question_prompts[4],"a"),
    question(question_prompts[5],"c"),
    question(question_prompts[6],"b"),
    question(question_prompts[7],"a"),
    question(question_prompts[8],"a"),
    question(question_prompts[9],"c"),
]




def run_test(questions):
    score = 0
    for question in questions:
        answer = input(question.prompt)
        if answer == question.answer:
            score += 1
            print("CORRECTO\n")
        else:
            print("INCORRECTO\n")

    print("Usted saco " + str(score) + "/" + str(len(questions)) + " correctas")


if __name__ == "__main__":

    run_test(questions)




