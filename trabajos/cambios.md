**En el contexto que existe es muy dificil que los usuarios carguen tantos datos para hacerse socios, debemos mejorar esa situacion, propongo que el ingreso de socio sea el sistema automatocamente crea un numero de socio sera correlativo a la cantidad existente a numero que figura en cantidad de socios, un nombre de usuario y clave validada como ahora, los demas campos de los datos pedidos no los mostraremos hasta el momento del canje de fichas. Entonces la logica cambia de esta forma en la tabla de usuarios no se elimina ningun campo existente, se agregaran los campos numero_de_socio, nombre_de_usuario, fichas_compradas, fichas_ganadas.

La logica cambiara de buscar todo por numero de documento a buscar todo por numero_de_socio, el funcionamiento del sistema sera igual pero por numero de socio.

Resumiendo: cambiamos el ingreso de “numero de documento” a “numero de socio” con la clave correspondiente, donde siempre aparecio numero de documento se usara numero de socio. Cuando ingresa un nuevo socio y termina de agregarse que le aparezca un cartel que diga su numero de socio es: {numero_de_socio}. En los ticket de las boletas en los ticket de compra de fichas en todos lados sera “numero de socio”.

Este ingreso es mas liviano y mas facil, las personas no quieren dar sus datos.

Importante: Cuando ingresen a canjear por la logica del negocio deberan completar todos los datos en forma obligatoria. Eso ocurrecuando se activael boton canje.

**
