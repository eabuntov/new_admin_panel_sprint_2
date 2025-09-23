from datetime import datetime

from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator, Page
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from uuid import UUID

from ...models import FilmWork, PersonFilmWork


class FilmWorkListApi(APIView):
    def get(self, request):
        """
        Handles the GET request for listing movies with pagination.
        """
        annotated_queryset = FilmWork.objects.annotate(
            genres_str=ArrayAgg(
            'genres__name',
            distinct=True
        ),
        actors=ArrayAgg(
            'personfilmwork__person__full_name',
            filter=Q(personfilmwork__role='actor'),
            distinct=True
        ),
        directors=ArrayAgg(
            'personfilmwork__person__full_name',
            filter=Q(personfilmwork__role='director'),
            distinct=True
        ),
        writers=ArrayAgg(
            'personfilmwork__person__full_name',
            filter=Q(personfilmwork__role='writer'),
            distinct=True
        )
        )
        try:
            page_string: str = request.query_params.get('page', '1')
            page = 1
            if page_string.isnumeric():
                page = int(page_string)
                if page < 1:
                    page = 1
        except ValueError:
            return Response({'error': 'Invalid page number. Must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        paginator = Paginator(annotated_queryset, per_page=50)  # Adjust per_page as needed
        movies = paginator.page(page)
        if page_string == 'last' or page > paginator.num_pages:
            page = paginator.num_pages
        data = {
            'count': FilmWork.objects.count(),
            'total_pages': paginator.num_pages,
            'prev': page - 1 if paginator.get_page(page).has_previous() else None,
            'next': page + 1 if paginator.get_page(page).has_next() else None,
            'results': form_movie_data(movies),
        }

        return Response(data)


def form_movie_data(movies: Page) -> list[dict[str, str]]:
    """
    Forms a dict representation of the FilmWork instances
    """
    data = []
    for movie in movies.object_list:
        data.append(
            {
                'id': str(movie.id),
                'title': movie.title,
                'description': movie.description,
                'creation_date': movie.creation_date.isoformat() if movie.creation_date else datetime.now().date().isoformat(),
                'rating': movie.rating or 0.0,
                'type': movie.type,
                'genres': movie.genres_str,
                'actors': movie.actors or [],
                'directors': movie.directors or [],
                'writers': movie.writers or [],
            }
        )
    return data

from datetime import datetime

def form_movie_data_single_query(movie_id: UUID) -> dict[str, str]:
    """
    Forms a dict representation of the FilmWork instance using a single query.

    Args:
        movie_id: The ID of the FilmWork to retrieve.

    Returns:
        A dict containing the movie data.
    """

    try:
        movie = FilmWork.objects.get(id=movie_id)
    except FilmWork.DoesNotExist:
        return None  # Or raise an exception, depending on your needs

    # Fetch all related data in a single query
    related_persons = PersonFilmWork.objects.filter(film_work_id=movie_id)

    actors = [person.person for person in related_persons.filter(role='actor')]
    directors = [person for person in related_persons.filter(role='director')]
    writers = [person for person in related_persons.filter(role='writer')]

    data = {
        'id': str(movie.id),
        'title': movie.title,
        'description': movie.description,
        'creation_date': movie.creation_date.isoformat() if movie.creation_date else datetime.now().date().isoformat(),
        'rating': movie.rating or 0.0,
        'type': movie.type,
        'genres': [str(genre) for genre in movie.genres.all()],
        'actors': [str(person) for person in actors],
        'directors': [str(person) for person in directors],
        'writers': [str(person) for person in writers],
    }
    return data



class FilmWorkDetailApi(APIView):
    def get(self, request, pk: str):
        """
        Handles the GET request for a specific movie by ID.
        """
        try:
            movie_id = UUID(pk)
            data = form_movie_data_single_query(movie_id)
        except ValueError:
            return Response({'error': 'Invalid UUID format'}, status=status.HTTP_404_NOT_FOUND)
        except FilmWork.DoesNotExist:
            return Response({'error': 'FilmWork not found'}, status=status.HTTP_404_NOT_FOUND)



        return Response(data)
