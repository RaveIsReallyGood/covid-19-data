import pandas as pd

from cowidev.utils.clean import clean_count
from cowidev.utils.web.scraping import get_soup
from cowidev.vax.utils.incremental import enrich_data, increment
from cowidev.vax.utils.dates import localdate


def read(source: str) -> pd.Series:
    return connect_parse_data(source)


def connect_parse_data(source: str) -> pd.Series:

    soup = get_soup(source)

    people_vaccinated = soup.find(class_="count-up").text
    people_vaccinated = clean_count(people_vaccinated)

    total_vaccinations = people_vaccinated

    return pd.Series(
        data={
            "total_vaccinations": total_vaccinations,
            "people_vaccinated": people_vaccinated,
        }
    )


def enrich_date(ds: pd.Series) -> pd.Series:
    date = localdate("Europe/Skopje")
    return enrich_data(ds, "date", date)


def enrich_location(ds: pd.Series) -> pd.Series:
    return enrich_data(ds, "location", "North Macedonia")


def enrich_vaccine(ds: pd.Series) -> pd.Series:
    return enrich_data(
        ds,
        "vaccine",
        "Oxford/AstraZeneca, Pfizer/BioNTech, Sinopharm/Beijing, Sputnik V",
    )


def enrich_source(ds: pd.Series, source: str) -> pd.Series:
    return enrich_data(ds, "source_url", source)


def pipeline(ds: pd.Series, source: str) -> pd.Series:
    return ds.pipe(enrich_date).pipe(enrich_location).pipe(enrich_vaccine).pipe(enrich_source, source)


def main(paths):
    source = "https://kovid19vakcinacija.mk/"
    data = read(source).pipe(pipeline, source)
    increment(
        paths=paths,
        location=data["location"],
        total_vaccinations=data["total_vaccinations"],
        people_vaccinated=data["people_vaccinated"],
        date=data["date"],
        source_url=data["source_url"],
        vaccine=data["vaccine"],
    )


if __name__ == "__main__":
    main()
