# Copyright 2023 Marcel Bollmann <marcel@bollmann.me>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from acl_anthology.collections import CollectionIndex
from acl_anthology.files import PDFReference
from acl_anthology.text import MarkupText
from acl_anthology.utils.xml import indent
from lxml import etree

from acl_anthology.collections.paper import (
    Paper,
    PaperDeletionType,
    PaperDeletionNotice,
    PaperErratum,
    PaperRevision,
)


@pytest.fixture
def index(anthology_stub):
    return CollectionIndex(anthology_stub)


def test_paper_minimum_attribs():
    paper_title = MarkupText.from_string("A minimal example")
    parent = None
    paper = Paper("42", parent, bibkey="nn-1900-minimal", title=paper_title)
    assert not paper.is_deleted
    assert paper.title == paper_title


test_cases_xml = (
    """<paper id="1">
  <title>Strings from neurons to language</title>
  <author><first>Tim</first><last>Fernando</last></author>
  <pages>1–10</pages>
  <url hash="61daae5b">2022.naloma-1.1</url>
  <bibkey>fernando-2022-strings</bibkey>
</paper>
""",
    """<paper id="9">
  <title>Briefly Noted</title>
  <url hash="166bd6c1">J89-1009</url>
  <bibkey>nn-1989-briefly</bibkey>
</paper>
""",
    """<paper id="6">
  <title>Domain Adaptation in Multilingual and Multi-Domain Monolingual Settings for Complex Word Identification</title>
  <author><first>George-Eduard</first><last>Zaharia</last></author>
  <author><first>Răzvan-Alexandru</first><last>Smădu</last></author>
  <author><first>Dumitru</first><last>Cercel</last></author>
  <author><first>Mihai</first><last>Dascalu</last></author>
  <pages>70-80</pages>
  <abstract>Complex word identification (CWI) is a cornerstone process towards proper text simplification. CWI is highly dependent on context, whereas its difficulty is augmented by the scarcity of available datasets which vary greatly in terms of domains and languages. As such, it becomes increasingly more difficult to develop a robust model that generalizes across a wide array of input examples. In this paper, we propose a novel training technique for the CWI task based on domain adaptation to improve the target character and context representations. This technique addresses the problem of working with multiple domains, inasmuch as it creates a way of smoothing the differences between the explored datasets. Moreover, we also propose a similar auxiliary task, namely text simplification, that can be used to complement lexical complexity prediction. Our model obtains a boost of up to 2.42% in terms of Pearson Correlation Coefficients in contrast to vanilla training techniques, when considering the CompLex from the Lexical Complexity Prediction 2021 dataset. At the same time, we obtain an increase of 3% in Pearson scores, while considering a cross-lingual setup relying on the Complex Word Identification 2018 dataset. In addition, our model yields state-of-the-art results in terms of Mean Absolute Error.</abstract>
  <url hash="23e260bb">2022.acl-long.6</url>
  <doi>10.18653/v1/2022.acl-long.6</doi>
  <video href="2022.acl-long.6.mp4"/>
  <bibkey>zaharia-etal-2022-domain</bibkey>
</paper>
""",
    """<paper id="max" ingest-date="2023-09-30">
  <title>This <fixed-case>P</fixed-case>aper Has All Fields That A Paper Can Have</title>
  <author><first/><last>None</last></author>
  <editor><first>Marcel</first><last>Bollmann</last></editor>
  <pages>0</pages>
  <abstract>
    <b>Look</b> at <i>this</i>!
  </abstract>
  <url hash="d6a71220">2023.fake-volume.max</url>
  <erratum id="1" hash="21a4921f">2023.fake-volume.maxe2</erratum>
  <revision id="1" href="2023.fake-volume.max" hash="21e2f21f"/>
  <revision id="2" href="2023.fake-volume.maxv2" hash="bc27f0f5" date="2023-10-03">Some explanation</revision>
  <doi>10.18653/v1/2023.fake-volume.max</doi>
  <language>Klingon</language>
  <note>This is not a real paper, obviously.</note>
  <attachment hash="a6a7a5a4" type="website">2023.fake-attachment</attachment>
  <attachment hash="12345678" type="software">2023.fake-software</attachment>
  <video href="2023.fake-video.mp4"/>
  <award>Most ridiculous entry</award>
  <removed date="2023-09-30">Removed immediately for being fake</removed>
  <bibkey>why-would-you-cite-this</bibkey>
  <pwccode url="https://github.com/acl-org/fake-repo" additional="false">acl-org/fake-repo</pwccode>
  <pwcdataset url="https://paperswithcode.com/dataset/fake-dataset">FaKe-DaTaSeT</pwcdataset>
</paper>
""",
)


@pytest.mark.parametrize("xml", test_cases_xml)
def test_paper_roundtrip_xml(xml):
    paper = Paper.from_xml(None, etree.fromstring(xml))
    out = paper.to_xml()
    indent(out)
    assert etree.tostring(out, encoding="unicode") == xml


test_cases_paperdeletionnotice = (
    (
        '<retracted date="2022-05-06">Paper was intended for the non-archival track.</retracted>',
        PaperDeletionType.RETRACTED,
        "Paper was intended for the non-archival track.",
        "2022-05-06",
    ),
    (
        '<removed date="1984-01-01">Scientific misconduct</removed>',
        PaperDeletionType.REMOVED,
        "Scientific misconduct",
        "1984-01-01",
    ),
)


@pytest.mark.parametrize("xml, type_, note, date", test_cases_paperdeletionnotice)
def test_paperdeletionnotice_from_xml(xml, type_, note, date):
    element = etree.fromstring(xml)
    notice = PaperDeletionNotice.from_xml(element)
    assert notice.type == type_
    assert notice.note == note
    assert notice.date == date


@pytest.mark.parametrize("xml, type_, note, date", test_cases_paperdeletionnotice)
def test_paperdeletionnotice_to_xml(xml, type_, note, date):
    notice = PaperDeletionNotice(type=type_, note=note, date=date)
    assert etree.tostring(notice.to_xml(), encoding="unicode") == xml


test_cases_papererratum = (
    (
        '<erratum id="1" hash="8eecd4c3" date="2022-09-20">P18-1188e1</erratum>',
        "1",
        "P18-1188e1",
        "8eecd4c3",
        "2022-09-20",
    ),
    (
        '<erratum id="42" hash="8edae19f">C12-1115e42</erratum>',
        "42",
        "C12-1115e42",
        "8edae19f",
        None,
    ),
)


@pytest.mark.parametrize(
    "xml, id_, pdf_name, pdf_checksum, date", test_cases_papererratum
)
def test_papererratum_from_xml(xml, id_, pdf_name, pdf_checksum, date):
    element = etree.fromstring(xml)
    erratum = PaperErratum.from_xml(element)
    assert erratum.id == id_
    assert erratum.pdf.name == pdf_name
    assert erratum.pdf.checksum == pdf_checksum
    assert erratum.date == date


@pytest.mark.parametrize(
    "xml, id_, pdf_name, pdf_checksum, date", test_cases_papererratum
)
def test_papererratum_to_xml(xml, id_, pdf_name, pdf_checksum, date):
    erratum = PaperErratum(
        id_, PDFReference(name=pdf_name, checksum=pdf_checksum), date=date
    )
    assert etree.tostring(erratum.to_xml(), encoding="unicode") == xml


test_cases_paperrevision = (
    (
        '<revision id="1" href="Q15-1022v1" hash="f16c56cd"/>',
        "1",
        "Q15-1022v1",
        "f16c56cd",
        None,
        None,
    ),
    (
        '<revision id="2" href="Q15-1022v2" hash="59f9673b">No description of the changes were recorded.</revision>',
        "2",
        "Q15-1022v2",
        "59f9673b",
        None,
        "No description of the changes were recorded.",
    ),
    (
        '<revision id="2" href="2020.pam-1.0v2" hash="7e1b77c7" date="2021-05-04">Author typo correction.</revision>',
        "2",
        "2020.pam-1.0v2",
        "7e1b77c7",
        "2021-05-04",
        "Author typo correction.",
    ),
)


@pytest.mark.parametrize(
    "xml, id_, pdf_name, pdf_checksum, date, note", test_cases_paperrevision
)
def test_paperrevision_from_xml(xml, id_, pdf_name, pdf_checksum, date, note):
    element = etree.fromstring(xml)
    revision = PaperRevision.from_xml(element)
    assert revision.id == id_
    assert revision.pdf.name == pdf_name
    assert revision.pdf.checksum == pdf_checksum
    assert revision.date == date
    assert revision.note == note


@pytest.mark.parametrize(
    "xml, id_, pdf_name, pdf_checksum, date, note", test_cases_paperrevision
)
def test_paperrevision_to_xml(xml, id_, pdf_name, pdf_checksum, date, note):
    revision = PaperRevision(
        id_, note=note, pdf=PDFReference(name=pdf_name, checksum=pdf_checksum), date=date
    )
    assert etree.tostring(revision.to_xml(), encoding="unicode") == xml
