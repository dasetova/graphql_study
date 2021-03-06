import graphene
from graphene_django import DjangoObjectType # custom type available in Graphene Django

from .models import Link, Vote # -> Importa el modelo que traduce la información de la base de datos
from users.schema import UserType
from django.db.models import Q

class LinkType(DjangoObjectType): #-> Definir el tipo para poder usarlo en queries, mutations and subscriptions
    class Meta:
        model = Link

class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class Query(graphene.ObjectType): # -> Definir aqui todos los queries
    links = graphene.List(
        LinkType,
        search=graphene.String(), #-> Parametro para filtrar
        first=graphene.Int(), # -> Parametro para paginacion
        skip=graphene.Int(), # -> Parametro para paginacion
        ) # -> Debe ser llamado así desde front, como links (va a ser el root del query), search permite filtrar
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs): # -> Función que resuelve la solucitud a links
        qs = Link.objects.all() # -> Obtener todos
        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            qs = qs.filter(filter) # -> Filtrar la busqueda de todos

        if skip:
            qs = qs[skip:] # -> Obviar
        
        if first:
            qs = qs[:first]

        return qs
    
    def resolve_votes(self, info, **kwargs): # -> Función que resuelve la solucitud a links
        return Vote.objects.all()

# Define una mutación con nombre CreateLink
class CreateLink(graphene.Mutation):
    # Campos que se devuelven como resultado de la mutación
    id = graphene.Int() 
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    # Campos que se reciben cuando se invoca la migración
    class Arguments:
        url = graphene.String()
        description = graphene.String()

    # Función que realiza realmente la mutación
    def mutate(self, info, url, description):
        user = info.context.user or None # Obtiene el usuario que esta autenticado

        link = Link(
            url=url, 
            description=description, 
            posted_by=user,
        )
        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by,
        )

class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            #raise Exception('You must be logged to vote!')
            raise GraphQLError('You must be logged to vote!')

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception('Invalid Link!')

        Vote.objects.create(
            user=user,
            link=link,
        )

        return CreateVote(user=user, link=link)

# Aquí se definen todas las mutaciones
class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field() # -> This is pointing to the createLink class
    create_vote = CreateVote.Field()


