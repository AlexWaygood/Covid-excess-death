from __future__ import annotations

from typing import Hashable, TypeVar, TYPE_CHECKING
import src.common_files.unchanging_constants as uc
import wbgapi.data as world_bank_data

if TYPE_CHECKING:
	T = TypeVar('T', bound=Hashable)
	from pandas import DataFrame


POPULATIONS = {
	'Gibraltar': '33,701',
	'San Marino': '33,860',
	'Liechtenstein': '38,019',
	'Andorra': '77,142',
	'Iceland': '360,563',
	'Malta': '504,062',
	'Luxembourg': '620,001',
	'Montenegro': '622,028',
	'Cyprus': '1,198,575',
	'Mauritius': '1,265,711',
	'Estonia': '1,326,898',
	'Kosovo': '1,788,878',
	'Latvia': '1,913,822',
	'North Macedonia': '2,083,459',
	'Slovenia': '2,088,385',
	'Moldova': '2,663,251',
	'Lithuania': '2,794,137',
	'Qatar': '2,832,067',
	'Albania': '2,854,191',
	'Jamaica': '2,948,279',
	'Armenia': '2,957,731',
	'Mongolia': '3,225,167',
	'Georgia': '3,720,161',
	'Croatia': '4,065,253',
	'Panama': '4,246,439',
	'Ireland': '4,934,040',
	'Oman': '4,974,986',
	'New Zealand': '4,979,300',
	'Costa Rica': '5,047,561',
	'Norway': '5,347,896',
	'Slovakia': '5,454,147',
	'Finland': '5,521,606',
	'Singapore': '5,703,569',
	'Denmark': '5,814,422',
	'Kyrgyzstan': '6,456,200',
	'Nicaragua': '6,545,502',
	'Serbia': '6,945,235',
	'Bulgaria': '6,975,761',
	'Paraguay': '7,044,636',
	'Switzerland': '8,575,280',
	'Austria': '8,879,920',
	'Israel': '9,054,000',
	'Belarus': '9,417,849',
	'Hungary': '9,771,141',
	'Azerbaijan': '10,024,283',
	'Sweden': '10,278,887',
	'Portugal': '10,286,263',
	'Czech Republic': '10,671,870',
	'Greece': '10,717,169',
	'Belgium': '11,502,704',
	'Bolivia': '11,513,100',
	'Tunisia': '11,694,719',
	'Guatemala': '16,604,026',
	'Netherlands': '17,344,874',
	'Ecuador': '17,373,662',
	'Kazakhstan': '18,513,673',
	'Chile': '18,952,038',
	'Romania': '19,366,221',
	'Australia': '25,365,745',
	'Peru': '32,510,453',
	'Uzbekistan': '33,580,350',
	'Canada': '37,593,384',
	'Poland': '37,965,475',
	'Ukraine': '44,386,203',
	'Spain': '47,133,521',
	'Colombia': '50,339,443',
	'S Korea': '51,709,098',
	'South Africa': '58,558,267',
	'Italy': '60,302,093',
	'UK': '66,836,327',
	'France': '67,055,854',
	'Thailand': '69,625,582',
	'Germany': '83,092,962',
	'Egypt': '100,388,073',
	'Philippines': '108,116,615',
	'Japan': '126,264,931',
	'Mexico': '127,575,529',
	'Russia': '144,406,261',
	'Brazil': '211,049,527',
	'US': '328,239,523'
}


class DictReturningKeys(dict):
	def __missing__(self, key: T) -> T:
		return key


WorldBankToFTCountryNames = DictReturningKeys({
	'Bosnia and Herzegovina': 'Bosnia',
	'Egypt, Arab Rep.': 'Egypt',
	'Hong Kong SAR': 'Hong Kong',
	'Kyrgyz Republic': 'Kyrgyzstan',
	'Macao SAR, China': 'Macao',
	'Russian Federation': 'Russia',
	'Korea, Rep.': 'S Korea',
	'Slovak Republic': 'Slovakia',
	'United Kingdom': 'UK',
	'United States': 'US'
})


def PopulationDatabase(*CountriesWithEstimates: str) -> DataFrame:
	return (
		world_bank_data
		.DataFrame(uc.WORLD_BANK_POPULATION, mrnev=1, labels=True)
		.pipe(lambda df: df.assign(Country=df.Country.map(WorldBankToFTCountryNames)))
		.pipe(lambda df: df.set_index(df.Country))
		[[uc.WORLD_BANK_POPULATION]]
		.pipe(lambda df: df.loc[df.index.isin(CountriesWithEstimates)])
		.astype({uc.WORLD_BANK_POPULATION: int})
	)


def NicelyPrintedPopulation(WorldBankData: DataFrame, name: str, LookupName: str) -> str:
	try:
		population = WorldBankData.at[name, uc.WORLD_BANK_POPULATION]
		pop = f'{(round(population / 1000) * 1000):,}' if population < 1_000_000 else f'{(population / 1_000_000):.3g}m'
		LegendName = f'{LookupName}, pop. {pop}'
	except KeyError:
		LegendName = LookupName

	return LegendName
