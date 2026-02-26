use redesocial;

drop table if exists comentario ;
drop table if exists likes ;
drop table if exists post ;
drop table if exists membrosgrupo ;
drop table if exists grupo ;
drop table if exists utilizador ;


create table membrosgrupo
(
   utilizadormembro   Integer   not null,
   grupoid   Integer   not null,
   dono   tinyint   null,
 
   constraint PK_membrosgrupo primary key (utilizadormembro,grupoid)
);
 
create table likes
(
   utilizadorlike   Integer   not null,
   postid   Integer   not null,
 
   constraint PK_likes primary key (utilizadorlike, postid)
);
 
create table utilizador
(
   emailutilizador   varchar(100)   null,
   nomeutilizador   varchar(100)   null,
   paisresidencia   varchar(50)   null,
   utilizadorid   Integer   not null,
 
   constraint PK_utilizador primary key (utilizadorid)
);
 
create table post
(
   autorpost   Integer   not null,
   postid   Integer   not null,
   textopost   text   null,
   datahorapost   datetime null,
 
   constraint PK_post primary key (postid)
);
 
create table grupo
(
   grupoid   Integer   not null,
   designacaogrupo   text   null,
   datacriacao   date   null,
 
   constraint PK_grupo primary key (grupoid)
);
 
create table comentario
(
   autorcomentario   Integer   not null,
   postcomentado   Integer   not null,
   comentarioid   Integer   not null,
   textocomentario   text   null,
   datahoracomentario   datetime null,
 
   constraint PK_comentario primary key (comentarioid)
);
 

alter table membrosgrupo
   add constraint FK_utilizador_membrosgrupo foreign key (utilizadormembro)
   references utilizador(utilizadorid)
   on delete cascade
   on update cascade
;

 
alter table membrosgrupo
   add constraint FK_grupo_membrosgrupo foreign key (grupoid)
   references grupo(grupoid)
   on delete cascade
   on update cascade
;


alter table likes
   add constraint FK_utilizador_likes_post_ foreign key (utilizadorlike)
   references utilizador(utilizadorid)
   on delete cascade
   on update cascade
; 
alter table likes
   add constraint FK_post_likes foreign key (postid)
   references post(postid)
   on delete cascade
   on update cascade
;
 


alter table post
   add constraint FK_post_Autoria foreign key (autorpost)
   references utilizador(utilizadorid)
   on delete restrict
   on update cascade
;
 
 
alter table comentario
   add constraint FK_comentario_utilizador foreign key (autorcomentario)
   references utilizador(utilizadorid)
   on delete restrict
   on update cascade
; 
alter table comentario
   add constraint FK_comentario_post foreign key (postcomentado)
   references post(postid)
   on delete restrict
   on update cascade
;



insert into utilizador values ('luis@iscte.pt', 'Luís Novas','Portugal',1 );
insert into utilizador values ('ana@iscte.pt', 'Ana Patrício','Portugal',2 );
insert into utilizador values ('carlos@iscte.pt', 'Carlos Monteiro','Brasil',3 );
insert into utilizador values ('isabel@iscte.pt', 'Isabel Fonseca','Angola',4 );
insert into utilizador values ('monica@iscte.pt', 'Mónica Martins','Portugal',5 );
insert into utilizador values ('pedro@iscte.pt', 'Pedro Cortêz','Portugal',6 );
insert into utilizador values ('paulo@iscte.pt', 'Paulo Vicente','Portugal',7 );
insert into utilizador values ('vera@iscte.pt', 'Vera Nogueira','Brasil',8 );
insert into utilizador values ('filipa@iscte.pt', 'Filipa Andrade','Portugal',9 );
insert into utilizador values ('jose@iscte.pt', 'José Raimundo','Portugal',10 );


insert into post values (1,1,'Amanhã ninguém pode faltar à festa da Vera!!',now());
insert into post values (2,10,'Os Linking Park ontem no Rock-In-Rio foram fantásticos.',now());

insert into grupo values(1,'Alunos 2º Ano ISTA',now());
insert into grupo values(2,'Fustsal ISCTE',now());
insert into MEMBROSGRUPO values (1,1,1);
insert into MEMBROSGRUPO values (1,2,0);
insert into MEMBROSGRUPO values (2,1,1);


