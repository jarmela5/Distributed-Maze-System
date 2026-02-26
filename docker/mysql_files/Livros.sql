create database livro;
use livro;
create table Autor 
(
    IDAutor              varchar(15) not null,
    Nome                 varchar(50),
    Nacionalidade        varchar(25),
    primary key (IDAutor)
);

create table Autoria 
(
    IDLivro              integer       not null,
    IDAutor              varchar(15)   not null,
    primary key (IDLivro, IDAutor)
);

create  index AUTORIA_FK on Autoria (
IDLivro ASC
);

create  index AUTORIA_FK2 on Autoria (
IDAutor ASC
);

create table Livro 
(
    IDLivro              integer    not null,
    Titulo               varchar(80),
    Editora              varchar(30),
    Edicao               integer,
    primary key (IDLivro)
);

alter table Autoria
   add foreign key FK_AUTORIA_AUTORIA_AUTOR (IDAutor)
      references Autor (IDAutor)
      on update restrict
      on delete restrict;

alter table Autoria
   add foreign key FK_AUTORIA_AUTORIA_LIVRO (IDLivro)
      references Livro (IDLivro)
      on update restrict
      on delete restrict;

insert into Livro values ( 00001 ,'As Cruzadas Vistas Pelos Árabes','Difel',  7 );
insert into Livro values ( 00002 ,'O Buraco Na Parede','Campo das Letras',  1 );
insert into Livro values ( 00003 ,'O Desejo De Kianda','Dom Quixote',  1 );
insert into Livro values ( 00004 ,'O Rochedo De Tanios','Difel',  1 );
insert into Livro values ( 00005 ,'E Se Tivesse A Bondade De Me Dizer Porquê ?','Edições Rolim',  1 );
insert into Livro values ( 00006 ,'Os Prisioneiros','Companhia das Letras',  4 );
insert into Livro values ( 00007 ,'Yaka','Dom Quixote',  2 );
insert into Livro values ( 00008 ,'Cavalos Em Fuga','Editorial Presença',  1 );
insert into Livro values ( 00009 ,'A Coleira Do Cão','Companhia das Letras',  4 );
insert into Livro values ( 00010 ,'Samarcanda','Difel',  4 );
insert into Livro values ( 00011 ,'Morte Em Pleno Verão','Relógio Dágua', null);
insert into Livro values ( 00012 ,'A Jangada De Pedra','Caminho',  1 );
insert into Livro values ( 00013 ,'Agosto','Dom Quixote',  1 );
insert into Livro values ( 00014 ,'Sede De Amar','Editorial Presença',  2 );
insert into Livro values ( 00015 ,'Escalas Do Levante','Difel',  1 );
insert into Livro values ( 00016 ,'Deste Mundo E Do Outro','Arcádia', null);
insert into Livro values ( 00017 ,'Lúcia McCartney','Companhia das Letras',  6 );
insert into Livro values ( 00018 ,'Os Meteoros','Dom Quixote',  1 );
insert into Livro values ( 00019 ,'Lituma Nos Andes','Dom Quixote',  1 );
insert into Livro values ( 00020 ,'Leão, O Africano','Bertrand',  4 );
insert into Livro values ( 00021 ,'A Geração Da Utopia','Dom Quixote',  2 );
insert into Livro values ( 00022 ,'História Do Cerco De Lisboa','Caminho',  1 );
insert into Livro values ( 00023 ,'O Selvagem Da Ópera','Companhia das Letras',  1 );
insert into Livro values ( 00024 ,'Horas Más','Queztal',  3 );
insert into Livro values ( 00025 ,'Os Jardins De Luz','Difel',  3 );
insert into Livro values ( 00026 ,'Romance Negro E Outras Histórias','Campo das Letras',  1 );
insert into Livro values ( 00027 ,'Uma Ceia De Amor','Dom Quixote',  1 );
insert into Livro values ( 00028 ,'O Caso Morel','Bertrand',  null );
insert into Livro values ( 00029 ,'Ensaio Sobre A Cegueira','Caminho',  1 );
insert into Livro values ( 00030 ,'O Século Primeiro Depois De Beatriz','Difel',  1 );
insert into Livro values ( 00031 ,'Feliz Ano Novo','Contexto',  null );
insert into Livro values ( 00032 ,'Gaspar, Belchior & Baltasar','Dom Quixote',  3 );
insert into Livro values ( 00033 ,'Um Deus Passeando Pela Brisa Da Tarde','Caminho',  4 );
insert into Livro values ( 00034 ,'Parábola Do Cágado Velho','Dom Quixote',  1 );
insert into Livro values ( 00035 ,'Giles & Jeanne','Dom Quixote',  20 );
insert into Livro values ( 00036 ,'O Cobrador','Companhia das Letras',  3 );
insert into Livro values ( 00037 ,'Adeus Princesa','Dom Quixote', null );
insert into Livro values ( 00038 ,'A Grande Arte','Edições 70',  1 );
insert into Livro values ( 00039 ,'A Casa Verde','Livros do Brasil',  null);
insert into Livro values ( 00040 ,'Bufo & Spallanzani','Companhia das Letras',  24 );
insert into Livro values ( 00041 ,'Lueji','Dom Quixote',  1 );
insert into Livro values ( 00042 ,'Vastas Emoções E Pensamentos Imperfeitos','Dom Quixote',  1 );
insert into Livro values ( 00043 ,'Conversa Na Catedral','Circulo de Leitores',  1 );
insert into Livro values ( 00044 ,'Agrião','Relógio Dágua',  1 );
insert into Livro values ( 00045 ,'Como Peixe Na Água','Dom Quixote',  1 );
insert into Livro values ( 00046 ,'A Cidade E Os Cães','Europa América', null);
insert into Livro values ( 00047 ,'A Paixão Do Conde De Fróis','Edições Rolim',  1 );
insert into Livro values ( 00048 ,'Olhos E Cão Azul','Queztal', null);
insert into Livro values ( 00049 ,'Domingo De Ramos','Circulo de Leitores',  1 );
insert into Livro values ( 00050 ,'A Inaudita Guerra Da Avenida Gago Coutinho','Caminho',  3 );
insert into Livro values ( 00051 ,'A Guerra Do Fim Do Mundo','Bertrand',  null);
insert into Livro values ( 00052 ,'A Incrível E Triste História Da Cândida Eréndira E Da Sua Avó Desalmada','Europa América',  2 );
insert into Livro values ( 00053 ,'Um Esquema','Edições Rolim',  2 );
insert into Livro values ( 00054 ,'Casos Do Beco Das Sardinheiras','Caminho',  2 );
insert into Livro values ( 00055 ,'Quem Matou Palomito Molero ?','Dom Quixote',  1 );
insert into Livro values ( 00056 ,'O General No Seu Labirinto','Dom Quixote',  1 );
insert into Livro values ( 00057 ,'Ponto Pé De Flor','Dom Quixote',  1 );
insert into Livro values ( 00058 ,'História De Mayta','Dom Quixote',  1 );
insert into Livro values ( 00059 ,'O Falador','Dom Quixote',  1 );
insert into Livro values ( 00060 ,'A Revoada','Queztal',  1 );
insert into Livro values ( 00061 ,'Do Amor E Outros Demónios','Dom Quixote',  1 );
insert into Livro values ( 00062 ,'Pantaleão E As Visitadoras','Europa América',  1 );
insert into Livro values ( 00063 ,'O Outono Do Patriarca','Europa América',  1 );
insert into Livro values ( 00064 ,'Os Cachoros Os Chefes','Bertrand',  1 );
insert into Livro values ( 00065 ,'Cem Anos De Solidão','Europa América',  1 );
insert into Livro values ( 00066 ,'A Tia Julia E O Escrevedor','Dom Quixote',  1 );
insert into Livro values ( 00067 ,'Elogio Da Madrasta','Dom Quixote',  1 );
insert into Livro values ( 00068 ,'As Aventuras De Miguel Littín Clandestino No Chile','O Jornal',  1 );
insert into Livro values ( 00069 ,'Ninguém Escreve Ao Coronel','Europa América',  1 );

insert into Autor values ('Carvalho','Mário de Carvalho','Português');
insert into Autor values ('Correia','Clara Pinto Corrêia','Português');
insert into Autor values ('Fonseca','Ruben Fonseca','Brasileiro');
insert into Autor values ('Llosa','Mario Vargas Llosa','Peruano');
insert into Autor values ('Maalouf','Amin Maalouf','Libanês');
insert into Autor values ('Marquez','Gabriel Garcia Marques','Colombiano');
insert into Autor values ('Mishima','Yukio Mishima','Japonês');
insert into Autor values ('Nerruda','Pablo Nerruda','Chileno');
insert into Autor values ('Pepetela','Pepetela','Angolano');
insert into Autor values ('Saramago','José Saramago','Português');
insert into Autor values ('Tournier','Michael Tournier','Françês');

insert into Autoria (IDAutor,IDLivro) values ('Carvalho',00005);
insert into Autoria (IDAutor,IDLivro) values ('Carvalho',00033);
insert into Autoria (IDAutor,IDLivro) values ('Carvalho',00047);
insert into Autoria (IDAutor,IDLivro) values ('Carvalho',00050);
insert into Autoria (IDAutor,IDLivro) values ('Carvalho',00054);
insert into Autoria (IDAutor,IDLivro) values ('Correia',00005);
insert into Autoria (IDAutor,IDLivro) values ('Correia',00037);
insert into Autoria (IDAutor,IDLivro) values ('Correia',00044);
insert into Autoria (IDAutor,IDLivro) values ('Correia',00049);
insert into Autoria (IDAutor,IDLivro) values ('Correia',00053);
insert into Autoria (IDAutor,IDLivro) values ('Correia',00057);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00002);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00006);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00009);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00013);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00017);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00023);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00026);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00028);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00031);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00036);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00038);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00040);
insert into Autoria (IDAutor,IDLivro) values ('Fonseca',00042);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00019);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00039);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00043);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00045);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00046);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00051);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00055);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00058);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00059);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00062);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00064);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00066);
insert into Autoria (IDAutor,IDLivro) values ('Llosa',00067);
insert into Autoria (IDAutor,IDLivro) values ('Maalouf',00001);
insert into Autoria (IDAutor,IDLivro) values ('Maalouf',00004);
insert into Autoria (IDAutor,IDLivro) values ('Maalouf',00010);
insert into Autoria (IDAutor,IDLivro) values ('Maalouf',00015);
insert into Autoria (IDAutor,IDLivro) values ('Maalouf',00020);
insert into Autoria (IDAutor,IDLivro) values ('Maalouf',00025);
insert into Autoria (IDAutor,IDLivro) values ('Maalouf',00030);
insert into Autoria (IDAutor,IDLivro) values ('Marquez',00024);
insert into Autoria (IDAutor,IDLivro) values ('Marquez',00048);
insert into Autoria (IDAutor,IDLivro) values ('Marquez',00052);
insert into Autoria (IDAutor,IDLivro) values ('Marquez',00056);
insert into Autoria (IDAutor,IDLivro) values ('Marquez',00060);
insert into Autoria (IDAutor,IDLivro) values ('Marquez',00061);
insert into Autoria (IDAutor,IDLivro) values ('Marquez',00063);
insert into Autoria (IDAutor,IDLivro) values ('Marquez',00065);
insert into Autoria (IDAutor,IDLivro) values ('Marquez',00068);
insert into Autoria (IDAutor,IDLivro) values ('Marquez',00069);
insert into Autoria (IDAutor,IDLivro) values ('Mishima',00008);
insert into Autoria (IDAutor,IDLivro) values ('Mishima',00011);
insert into Autoria (IDAutor,IDLivro) values ('Mishima',00014);
insert into Autoria (IDAutor,IDLivro) values ('Pepetela',00003);
insert into Autoria (IDAutor,IDLivro) values ('Pepetela',00007);
insert into Autoria (IDAutor,IDLivro) values ('Pepetela',00021);
insert into Autoria (IDAutor,IDLivro) values ('Pepetela',00034);
insert into Autoria (IDAutor,IDLivro) values ('Pepetela',00041);
insert into Autoria (IDAutor,IDLivro) values ('Saramago',00012);
insert into Autoria (IDAutor,IDLivro) values ('Saramago',00016);
insert into Autoria (IDAutor,IDLivro) values ('Saramago',00022);
insert into Autoria (IDAutor,IDLivro) values ('Saramago',00029);
insert into Autoria (IDAutor,IDLivro) values ('Tournier',00018);
insert into Autoria (IDAutor,IDLivro) values ('Tournier',00027);
insert into Autoria (IDAutor,IDLivro) values ('Tournier',00032);
insert into Autoria (IDAutor,IDLivro) values ('Tournier',00035);

