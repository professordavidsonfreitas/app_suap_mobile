from models.app_version import (AppVersion)


async def obter_ultima_versao(db):

    return db.query(
        AppVersion
    ).filter(
        AppVersion.ativa == True
    ).order_by(
        AppVersion.build.desc()
    ).first()


async def criar_versao(
    db,
    dados
):

    versao = AppVersion(
        versao=dados.versao,
        build=dados.build,
        obrigatoria=dados.obrigatoria,
        apk_url=dados.apk_url,
        descricao=dados.descricao
    )

    db.add(versao)
    db.commit()
    db.refresh(versao)

    return versao